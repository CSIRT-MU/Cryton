import re
from snek_sploit import Error as MSFError, RPCError as MSFRPCError

from cryton.lib.metasploit import MetasploitClientUpdated
from cryton.lib.utility.module import ModuleBase, ModuleOutput, Result


class Module(ModuleBase):
    SCHEMA = {
        "type": "object",
        "description": "Arguments for the `metasploit` module.",
        "OneOf": [
            {
                "properties": {
                    "module_name": {"type": "string", "description": "Name of the Metasploit module to use."},
                    "datastore": {"type": "object", "description": "Datastore options to use for the execution."},
                    "timeout": {"type": "integer", "description": "The maximum time to wait for the output"},
                },
                "additionalProperties": False,
                "required": ["module_name"],
            },
            {
                "properties": {
                    "commands": {
                        "type": "array",
                        "description": "Custom set of commands to execute in an order.",
                        "items": {"type": "string"},
                    },
                    "timeout": {"type": "integer", "description": "The maximum time to wait for the output"},
                },
                "additionalProperties": False,
                "required": ["commands"],
            },
        ],
    }

    def __init__(self, arguments: dict):
        super().__init__(arguments)
        self._msf_client = MetasploitClientUpdated(log_in=False)

        self._commands: list[str] = self._arguments.get("commands", [])
        self._module_name: str | None = self._arguments.get("module_name", None)
        self._datastore: dict[str, str | int] = {
            key.upper(): value for key, value in self._arguments.get("datastore", {}).items()
        }
        self._payload_name: str | None = self._datastore.pop("PAYLOAD", None)
        self._timeout: int | None = self._arguments.get("timeout", None)

    def check_requirements(self) -> None:
        """
        Check whether the MSF connection is working.
        :raise ConnectionError: In case the MSF is unreachable
        :raise RuntimeError: In case of wrong credentials
        :return: None
        """
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
        """
        Execute module or a set of commands in the MSF console.
        :return: Module output
        """
        commands = self._get_commands()
        output = self._run_commands(commands)
        self._parse_results(output)

        return self._data

    def _get_commands(self) -> list[str]:
        """
        Create a set of commands that will be executed in the MSF console.
        :return: Set of commands
        """
        if self._commands:
            return self._commands

        commands: list[str] = list()
        commands.append(f"use {self._module_name}")

        if self._payload_name:
            commands.append(f"set PAYLOAD {self._payload_name}")

        for name, value in self._datastore.items():
            commands.append(f"set {name} {value}")

        # `-z`/`--no-interact` -> don't interact with the created session
        # The usage of `--no-interact` prohibits to run post modules
        commands.append("run -z")

        return commands

    def _run_commands(self, commands: list[str]) -> str:
        """
        Create an MSF console, join the commands, and run it.
        :param commands: List of commands to execute in the MSF console chronologically
        :return: Execution output
        """
        console = self._msf_client.consoles.create()
        output = console.execute("\n".join(commands), self._timeout)
        console.destroy()

        return output

    def _parse_results(self, output: str) -> None:
        """
        Save output, session, and decide the result.
        :param output: Execution output
        :return: None
        """
        self._data.output = output

        match_session = re.search(r"\[\*] .+ session (\d+) opened \(.+\) at", output)
        if match_session and match_session.groups():
            self._data.serialized_output["session_id"] = int(match_session.groups()[-1])
        elif re.search(r"Exploit failed \(.+\)", output):
            return
        elif re.search(r"\[\*] Exploit completed, but no session was created", output):
            return

        self._data.result = Result.OK

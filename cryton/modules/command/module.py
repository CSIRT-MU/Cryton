import re
import json
import subprocess
from snek_sploit import Error as MSFError, RPCError as MSFRPCError, SessionType

from cryton.lib.metasploit import MetasploitClientUpdated
from cryton.lib.utility.module import ModuleBase, ModuleOutput, Result


class Module(ModuleBase):
    _SCHEMA = {
        "type": "object",
        "description": "Arguments for the `command` module.",
        "properties": {
            "command": {"type": "string", "description": "Command to run with syntax as in command line."},
            "timeout": {"type": "integer", "description": "Timeout for the command (**in seconds**)."},
            "serialize_output": {
                "type": "boolean",
                "description": "Try to parse the output of the command into `serialized_output`.",
            },
            "session_id": {"type": "integer", "description": "ID of the session to use."},
            "force_shell": {
                "type": "boolean",
                "description": "Run the `command` in shell even in a Meterpreter session.",
            },
        },
        "required": ["command"],
        "additionalProperties": False,
    }

    def __init__(self, arguments: dict):
        super().__init__(arguments)
        self._msf_client = MetasploitClientUpdated(log_in=False)

        self._command: str = self._arguments["command"]
        self._timeout: int | None = self._arguments.get("timeout", None)
        self._serialize_output_flag: bool = self._arguments.get("serialize_output", False)
        self._session_id: int | None = self._arguments.get("session_id", None)
        self._force_shell: int | None = self._arguments.get("force_shell", True)

    def check_requirements(self) -> None:
        """
        In case the `session_id` is defined, check for MSF RPC connection.
        :return: None
        """
        if not self._session_id:
            return

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
        Execute a command locally or in a Metasploit session.
        :return:
        """
        if self._session_id:
            try:
                session = self._msf_client.sessions.get(self._session_id)
                if session.info.type == SessionType.METERPRETER:
                    if self._force_shell:
                        command = self._command.split(" ")
                        process_output = session.execute_in_shell(command[0], command[1:], self._timeout)
                    else:
                        process_output = session.execute(self._command, self._timeout)
                else:
                    process_output = session.execute(self._command, self._timeout)
            except Exception as ex:
                self._data.output += str(ex)
                return self._data

            self._data.result = Result.OK
            self._data.output += process_output

        else:
            try:
                process = subprocess.run(
                    self._command, timeout=self._timeout, capture_output=True, shell=True, check=True
                )
            except subprocess.TimeoutExpired:
                self._data.output += "Command execution timed out."
                return self._data
            except subprocess.CalledProcessError as ex:
                self._data.output += ex.stderr.decode("utf-8")
                return self._data
            except Exception as ex:
                self._data.output += str(ex)
                return self._data

            process_output = process.stdout.decode("utf-8")
            process_error = process.stderr.decode("utf-8")

            self._data.output += f"{process_output}\n{process_error}"
            if not process_error:
                self._data.result = Result.OK

        if self._serialize_output_flag:
            try:
                self._data.serialized_output = self._serialize_output(process_output)
            except TypeError as ex:
                self._data.output += f"\n{ex}"
                self._data.result = Result.FAIL

        return self._data

    def _sanitize_output(self, output: str) -> str:
        """
        Remove command unrelated output from session execution.
        :param output:
        :return: Sanitized output
        """
        # Commands executed inside of a Meterpreter session in a channel.
        output = re.sub(r"Process \d+ created\.\nChannel \d+ created\.\n", "", output, 1)
        # This is basically just a guessing game when it comes to Windows shells.
        # It will get better with more data to test.
        # Tested cases:
        #   cmd: Powershell -C "whoami | ConvertTo-Json"
        output = output.replace(self._command, "", 1).rsplit("\r\n\r\n", 1)[0]

        return output

    def _serialize_output(self, output: str) -> list | dict:
        """
        Try to serialize the output.
        :param output: String containing a valid JSON
        :return: Serialized output
        :exception TypeError: If the supplied output is not a valid json
        """
        if self._session_id:
            output = self._sanitize_output(output)

        try:
            serialized_output = json.loads(output)
        except (json.JSONDecodeError, TypeError):
            raise TypeError("Unable to serialize the output - invalid JSON.")

        if isinstance(serialized_output, str):
            return {"auto_serialized": serialized_output}
        elif isinstance(serialized_output, dict) or isinstance(serialized_output, list):
            return serialized_output
        else:
            return {}

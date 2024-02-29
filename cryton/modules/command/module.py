import json
import subprocess
from typing import Union

from cryton.worker.utility.util import Metasploit
from cryton.lib.utility.module import ModuleBase, ModuleOutput, Result


# TODO: add tests
class Module(ModuleBase):
    SCHEMA = {
        "type": "object",
        "description": "Arguments for the `command` module.",
        "properties": {
            "command": {
                "type": "string",
                "description": "Command to run with syntax as in command line."
            },
            "end_checks": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "Strings to check in the output to determine whether the command has finished."
                }
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout for the command (**in seconds**)."
            },
            "minimal_execution_time": {
                "type": "integer",
                "description": "Time (**in seconds**) to wait for the output before reading from the shell."
            },
            "serialize_output": {
                "type": "boolean",
                "description": "Try to parse the output of the command into `serialized_output`."
            },
            "session_id": {
                "type": "integer",
                "description": ""
            }
        },
        "required": ["command"],
        "additionalProperties": False
    }

    def __init__(self, arguments: dict):
        super().__init__(arguments)

        self._command: str = self._arguments["command"]
        self._end_checks: list[str] = self._arguments.get("end_checks")
        self._timeout: int = self._arguments.get("timeout")
        self._minimal_execution_time: int = self._arguments.get("minimal_execution_time")
        self._serialize_output: bool = self._arguments.get("serialize_output", False)
        self._session_id: int = self._arguments.get("session_id")

    def check_requirements(self) -> None:
        """
        In case the `session_id` is defined, check for MSF RPC connection.
        :return: None
        """
        if self._session_id is not None and not Metasploit().is_connected():
            raise ConnectionError("Could not connect to MSF RPC.")

    def execute(self) -> ModuleOutput:
        """
        Check if the user defined a `session_id`
        :return:
        """
        if self._session_id is not None:
            try:
                msf = Metasploit()
                process_output = msf.execute_in_session(
                    self._command,
                    str(self._session_id),
                    self._timeout,
                    self._end_checks,
                    minimal_execution_time=self._minimal_execution_time
                )
            except Exception as ex:
                self._data.output += str(ex)
                return self._data

            self._data.result = Result.OK
            self._data.output += process_output

        else:
            try:
                process = subprocess.run(
                    self._command,
                    timeout=self._timeout,
                    capture_output=True,
                    shell=True,
                    check=True
                )
            except subprocess.TimeoutExpired:
                self._data.output += "Command execution timed out"
                return self._data
            except subprocess.CalledProcessError as ex:
                self._data.output += ex.stderr.decode("utf-8")
                return self._data
            except Exception as ex:
                self._data.output += str(ex)
                return self._data

            process_output = process.stdout.decode("utf-8")
            process_error = process.stderr.decode("utf-8")

            self._data.output += f"{process_output}{chr(10)}{process_error}"
            if not process_error:
                self._data.result = Result.OK

        if self._serialize_output:
            try:
                self._data.serialized_output = self.serialize_output(process_output)
            except TypeError as ex:
                self._data.output += f"{chr(10)}{ex}"
                self._data.result = Result.FAIL

        return self._data

    def serialize_output(self, output: str) -> Union[list, dict]:
        """
        Try to serialize the output.
        :param output: String containing a valid JSON
        :return: Serialized output
        :exception TypeError: If the supplied output is not a valid json
        """
        # This is basically just a guessing game when it comes to Windows shells.
        # It will get better with more data to test.
        # Tested cases:
        #   cmd: Powershell -C "whoami | ConvertTo-Json"
        if self._session_id is not None:
            processed_output = output.replace(self._command, "", 1).rsplit("\r\n\r\n", 1)[0]
        else:
            processed_output = output

        try:
            serialized_output = json.loads(processed_output)
        except (json.JSONDecodeError, TypeError):
            raise TypeError("Unable to serialize the output - invalid JSON.")

        if isinstance(serialized_output, str):
            serialized_output = {"auto_serialized": serialized_output}

        return serialized_output

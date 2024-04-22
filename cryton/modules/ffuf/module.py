import os
import json
import subprocess
from uuid import uuid1

from cryton.lib.utility.module import ModuleBase, ModuleOutput, Result


class Module(ModuleBase):
    SCHEMA = {
        "type": "object",
        "description": "Arguments for the `ffuf` module.",
        "oneOf": [
            {
                "properties": {
                    "target": {"type": "string", "description": "Scan target."},
                    "wordlist": {"type": "string", "description": "The wordlist for fuzzing the webserver."},
                    "options": {"type": "string", "description": "Additional FFUF parameters."},
                    "serialize_output": {"type": "boolean", "description": "Use FFUF's serialization."},
                },
                "required": ["target", "wordlist"],
                "additionalProperties": False,
            },
            {
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to run with syntax as in command line (with executable).",
                    }
                },
                "required": ["command"],
                "additionalProperties": False,
            },
        ],
    }

    def __init__(self, arguments: dict):
        super().__init__(arguments)

        self._command = self._arguments.get("command")
        self._target = self._arguments.get("target")
        self._wordlist = self._arguments.get("wordlist")
        self._options = self._arguments.get("options", "")
        self._serialize_output = self._arguments.get("serialize_output", True)
        self._tmp_file = f"/tmp/cryton-report-ffuf-{uuid1()}"

    def check_requirements(self) -> None:
        if self._command is not None:
            return

        if not os.path.isfile(self._wordlist):
            raise OSError("Unable to access the defined wordlist.")

        try:
            subprocess.run("ffuf")
        except FileNotFoundError:
            raise OSError("Unable to find ffuf.")

    def execute(self) -> ModuleOutput:
        command = self._command.split(" ") if self._command is not None else self._build_command()

        try:
            process = subprocess.run(command, capture_output=True, check=True)
        except subprocess.CalledProcessError as ex:
            self._data.output += f"{ex.stdout.decode('utf-8')}\n{ex.stderr.decode('utf-8')}"
            return self._data
        except Exception as ex:
            self._data.output += str(ex)
            return self._data

        process_output = process.stdout.decode("utf-8")
        process_error = process.stderr.decode("utf-8")

        self._data.output += f"{process_output}\n{process_error}"

        if self._serialize_output and os.path.isfile(self._tmp_file):
            try:
                with open(self._tmp_file) as f:
                    self._data.serialized_output = json.load(f)
            except (OSError, json.JSONDecodeError) as ex:
                self._data.output += f"Unable to get the serialized data. Reason: {ex}"
                return self._data

            try:
                os.remove(self._tmp_file)
            except OSError:
                pass

        if "Encountered error" not in self._data.output:
            self._data.result = Result.OK

        return self._data

    def _build_command(self) -> list[str]:
        command = ["ffuf", "-w", self._wordlist, "-u", self._target]
        if self._serialize_output:
            command += ["-of", "json", "-o", self._tmp_file]
        if self._options:
            command += self._options.split(" ")

        return command

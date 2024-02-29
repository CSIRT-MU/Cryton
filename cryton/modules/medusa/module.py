import os
import subprocess
from uuid import uuid1

from cryton.lib.utility.module import ModuleBase, ModuleOutput, Result


# TODO: add tests
class Module(ModuleBase):
    SCHEMA = {
        "type": "object",
        "description": "Arguments for the `medusa` module.",
        "oneOf": [
            {
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Bruteforce target."
                    },
                    "mod": {
                        "type": "string",
                        "description": "mod (service) to attack."
                    },
                    "tasks": {
                        "type": "integer",
                        "description": "Number of login pairs tested concurrently."
                    },
                    "options": {
                        "type": "string",
                        "description": "Additional Medusa parameters."
                    },
                    "credentials": {
                        "type": "object",
                        "description": "",
                        "properties": {
                            "username": {
                                "type": "string",
                                "description": "Username."
                            },
                            "username_file": {
                                "type": "string",
                                "description": "Absolute path to file with usernames."
                            },
                            "password": {
                                "type": "string",
                                "description": "Password."
                            },
                            "password_file": {
                                "type": "string",
                                "description": "Absolute path to file with passwords."
                            },
                            "combo_file": {
                                "type": "string",
                                "description": "Absolute path to file with username and password pairs."
                            }
                        },
                        "oneOf": [
                            {"required": ["combo_file"]},
                            {"required": ["username", "password"]},
                            {"required": ["username", "password_file"]},
                            {"required": ["username_file", "password"]},
                            {"required": ["username_file", "password_file"]},
                        ],
                        "additionalProperties": False
                    }
                },
                "required": ["target", "credentials"],
                "additionalProperties": False
            },
            {
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to run with syntax as in command line (with executable)."
                    }
                },
                "required": ["command"],
                "additionalProperties": False
            }
        ]
    }

    def __init__(self, arguments: dict):
        super().__init__(arguments)

        self._target = self._arguments.get("target")
        self._mod = self._arguments.get("mod", "ssh")
        self._tasks = self._arguments.get("tasks", 4)
        self._options = self._arguments.get("options", "")
        self._credentials: dict = self._arguments.get("credentials")
        self._command = self._arguments.get("command")
        self._tmp_file = f"/tmp/cryton-report-ffuf-{uuid1}"

    def check_requirements(self) -> None:
        if self._command is not None:
            return

        if (combo_file := self._credentials.get("combo_file")) and not os.path.isfile(combo_file):
            raise OSError("Unable to access combo_file.")
        else:
            if (username_file := self._credentials.get("username_file")) and not os.path.isfile(username_file):
                raise OSError("Unable to access username_file.")

            if (password_file := self._credentials.get("password_file")) and not os.path.isfile(password_file):
                raise OSError("Unable to access password_file.")

        try:
            subprocess.run("medusa")
        except FileNotFoundError:
            raise OSError("Unable to find medusa.")

    def execute(self) -> ModuleOutput:
        command = self._command.split(" ") if self._command is not None else self._build_command()

        try:
            process = subprocess.run(command, capture_output=True, check=True)
        except subprocess.CalledProcessError as ex:
            self._data.output += f"{ex.stdout}{chr(10)}{ex.stderr}"
            return self._data
        except Exception as ex:
            self._data.output += str(ex)
            return self._data

        process_output = process.stdout.decode("utf-8")
        process_error = process.stderr.decode("utf-8")

        if "ACCOUNT FOUND:" in process_output and "[SUCCESS]" in process_output:
            self._data.result = Result.OK
            self._data.serialized_output = self._parse_credentials(process_output)

        self._data.output += f"{process_output}{chr(10)}{process_error}"

        return self._data

    def _build_command(self):
        command = ["medusa", "-h", self._target, "-t", str(self._tasks), "-M", self._mod]

        if combo_file := self._credentials.get("combo_file"):
            command += ["-C", combo_file]
        else:
            if username := self._credentials.get("username"):
                command += ["-u", username]
            elif username_file := self._credentials.get("username_file"):
                command += ["-U", username_file]

            if password := self._credentials.get("password"):
                command += ["-p", password]
            elif password_file := self._credentials.get("password_file"):
                command += ["-P", password_file]

        return command

    @staticmethod
    def _parse_credentials(medusa_output: str) -> dict:
        """
        Parse found credentials from medusa output.

        :param medusa_output: Stdout of medusa bruteforce
        :return: Found username and password credentials
        """
        json_credentials = []
        medusa_output_lines = medusa_output.split("\n")
        for row in medusa_output_lines:
            if "ACCOUNT FOUND:" in row:
                found_username = ""
                found_password = ""
                row_split = row.split(" ")
                for word in row_split:
                    if word == "User:":
                        found_username = (row_split[row_split.index(word) + 1]).strip()
                    if word == "Password:":
                        found_password = (row_split[row_split.index(word) + 1]).strip()
                json_credentials.append({"username": str(found_username), "password": str(found_password)})

        if json_credentials:
            json_credentials = {"username": json_credentials[0]["username"],
                                "password": json_credentials[0]["password"],
                                "all_credentials": json_credentials}
        return json_credentials

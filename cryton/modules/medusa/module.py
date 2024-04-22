import os
import subprocess

from cryton.lib.utility.module import ModuleBase, ModuleOutput, Result


class Module(ModuleBase):
    SCHEMA = {
        "definitions": {
            "username": {"type": "string", "description": "Username."},
            "username_file": {"type": "string", "description": "Absolute path to file with usernames."},
            "password": {"type": "string", "description": "Password."},
            "password_file": {"type": "string", "description": "Absolute path to file with passwords."},
            "combo_file": {"type": "string", "description": "Absolute path to file with username and password pairs."},
        },
        "type": "object",
        "description": "Arguments for the `medusa` module.",
        "oneOf": [
            {
                "properties": {
                    "target": {"type": "string", "description": "Bruteforce target."},
                    "mod": {"type": "string", "description": "mod (service) to attack."},
                    "tasks": {"type": "integer", "description": "Number of login pairs tested concurrently."},
                    "options": {"type": "string", "description": "Additional Medusa parameters."},
                    "credentials": {
                        "type": "object",
                        "description": "",
                        "oneOf": [
                            {
                                "properties": {"combo_file": {"$ref": "#/definitions/combo_file"}},
                                "minProperties": 1,
                                "additionalProperties": False,
                            },
                            {
                                "properties": {
                                    "username": {"$ref": "#/definitions/username"},
                                    "password": {"$ref": "#/definitions/password"},
                                },
                                "minProperties": 2,
                                "additionalProperties": False,
                            },
                            {
                                "properties": {
                                    "username": {"$ref": "#/definitions/username"},
                                    "password_file": {"$ref": "#/definitions/password_file"},
                                },
                                "minProperties": 2,
                                "additionalProperties": False,
                            },
                            {
                                "properties": {
                                    "username_file": {"$ref": "#/definitions/username_file"},
                                    "password": {"$ref": "#/definitions/password"},
                                },
                                "minProperties": 2,
                                "additionalProperties": False,
                            },
                            {
                                "properties": {
                                    "username_file": {"$ref": "#/definitions/username_file"},
                                    "password_file": {"$ref": "#/definitions/password_file"},
                                },
                                "minProperties": 2,
                                "additionalProperties": False,
                            },
                        ],
                    },
                },
                "required": ["target", "credentials"],
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

        self._target = self._arguments.get("target")
        self._mod = self._arguments.get("mod", "ssh")
        self._tasks = self._arguments.get("tasks", 4)
        self._options = self._arguments.get("options", "")
        self._credentials: dict = self._arguments.get("credentials")
        self._command = self._arguments.get("command")

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
            self._data.output += f"{ex.stdout.decode('utf-8')}\n{ex.stderr.decode('utf-8')}"
            return self._data
        except Exception as ex:
            self._data.output += str(ex)
            return self._data

        process_output = process.stdout.decode("utf-8")
        process_error = process.stderr.decode("utf-8")

        self._data.output += f"{process_output}\n{process_error}"

        if "ACCOUNT FOUND:" in process_output and "[SUCCESS]" in process_output:
            self._data.result = Result.OK
            self._data.serialized_output = self._parse_credentials(process_output)

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

        if self._options:
            command += self._options.split(" ")

        return command

    @staticmethod
    def _parse_credentials(medusa_output: str) -> dict:
        """
        Parse found credentials from medusa output.

        :param medusa_output: Stdout of medusa bruteforce
        :return: Found username and password credentials
        """
        # TODO: replace with regex
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
            json_credentials = {
                "username": json_credentials[0]["username"],
                "password": json_credentials[0]["password"],
                "all_credentials": json_credentials,
            }
        return json_credentials

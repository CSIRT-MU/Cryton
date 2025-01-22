import subprocess
import json

from cryton.lib.utility.module import ModuleBase, ModuleOutput, Result


# TODO: this module is only updated to work with the new rules, it's not reworked
#  - update validation (mainly descriptions)
#  - update check_requirements
#  - rework the module
#  - add tests
class Module(ModuleBase):
    _SCHEMA = {
        "type": "object",
        "description": "Arguments for the `wpscan` module.",
        "oneOf": [
            {
                "properties": {
                    "target": {"type": "string"},
                    "options": {"type": "string"},
                    "api_token": {"type": "string"},
                    "serialize_output": {"type": "boolean"},
                },
                "required": ["target"],
                "additionalProperties": False,
            },
            {
                "properties": {"command": {"type": "string", "description": "Command to run (with executable)."}},
                "required": ["command"],
                "additionalProperties": False,
            },
        ],
    }

    def __init__(self, arguments: dict):
        super().__init__(arguments)

    def check_requirements(self) -> None:
        pass

    def execute(self) -> ModuleOutput:
        wpscan_command = parse_command(self._arguments)

        try:
            wpscan_run = subprocess.run(wpscan_command, capture_output=True)
        except OSError as err:
            self._data.output = f"Check if your command starts with 'wpscan'. Original error: {str(err)}"
            return self._data
        except subprocess.SubprocessError as err:
            self._data.output = f"WPScan couldn't start. Original error: {str(err)}"
            return self._data

        wpscan_std_out = wpscan_run.stdout.decode("utf-8")
        wpscan_std_err = wpscan_run.stderr.decode("utf-8")

        try:
            self._data.serialized_output = json.loads(wpscan_std_out)
        except json.decoder.JSONDecodeError:
            self._data.output = wpscan_std_out

        failure_strings = [
            "unrecognized option",
            "option requires an argument",
            "seems to be down",
            "but does not seem to be running WordPress.",
            "has not been found",
            "Scan Aborted",
        ]
        if not any(failure_string in wpscan_std_out for failure_string in failure_strings):
            self._data.result = Result.OK

        if wpscan_std_err:
            self._data.output += wpscan_std_err

        return self._data


def parse_command(arguments) -> list[str]:
    if "command" in arguments:
        return arguments["command"].split(" ")

    serialized_output: bool = arguments.get("serialized_output", True)
    target: str = arguments.get("target")
    command_options: str = arguments.get("options")
    api_token: str = arguments.get("api_token")

    command = ["wpscan"]

    report_type = "cli"
    if serialized_output:
        report_type = "json"

    command += ["--url", target, "-f", report_type]

    if api_token:
        command += ["--api-token", api_token]

    if command_options is not None:
        command += command_options.split(" ")

    return command

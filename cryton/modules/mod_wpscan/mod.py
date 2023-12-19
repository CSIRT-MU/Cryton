import subprocess
import json
from schema import Schema, Optional, SchemaError, Or
from typing import List
from cryton.worker.utility.module_util import OUTPUT, SERIALIZED_OUTPUT, RETURN_CODE


def validate(arguments: dict) -> int:
    """
    Validate input values for the execute function

    :param arguments: Arguments for module execution
    :return: 0 If arguments are valid
    :raises: Schema Exception
    """
    conf_schema = Schema(Or(
        {
            'target': str,
            Optional('options'): str,
            Optional('api_token'): str,
            Optional('serialized_output'): bool,
        },
        {
            "custom_command": str
        },
        only_one=True)
    )

    conf_schema.validate(arguments)

    return 0


def parse_command(arguments) -> List[str]:
    if "custom_command" in arguments:
        return arguments["custom_command"].split(" ")

    serialized_output: bool = arguments.get('serialized_output', True)
    target: str = arguments.get('target')
    command_options: str = arguments.get('options')
    api_token: str = arguments.get('api_token')

    command = ["wpscan"]

    report_type = "cli"
    if serialized_output:
        report_type = "json"

    command += ["--url", target, "-f", report_type]

    if api_token:
        command += ["--api-token", api_token]

    if command_options is not None:
        command += command_options.split(' ')

    return command


def execute(arguments: dict) -> dict:
    """
    Executes wpscan scan via command with given arguments.
    :param dict arguments: dictionary of mandatory subdictionary 'arguments' and other optional elements
    :return: ret_vals: dictionary with following values:

        * ret: 0 in success, other number in failure,

        * value: return value, usually stdout,

        * output: error message, if any
    """
    ret_vals = {
        RETURN_CODE: -1,
        OUTPUT: "",
        SERIALIZED_OUTPUT: {}
    }

    try:
        validate(arguments)
    except SchemaError as err:
        ret_vals["output"] = str(err)
        return ret_vals

    wpscan_command = parse_command(arguments)

    try:
        wpscan_run = subprocess.run(wpscan_command, capture_output=True)
    except OSError as err:
        ret_vals[OUTPUT] = f"Check if your command starts with 'wpscan'. Original error: {str(err)}"
        return ret_vals
    except subprocess.SubprocessError as err:
        ret_vals[OUTPUT] = f"WPScan couldn't start. Original error: {str(err)}"
        return ret_vals

    wpscan_std_out = wpscan_run.stdout.decode('utf-8')
    wpscan_std_err = wpscan_run.stderr.decode('utf-8')

    try:
        ret_vals[SERIALIZED_OUTPUT] = json.loads(wpscan_std_out)
    except json.decoder.JSONDecodeError:
        ret_vals[OUTPUT] = wpscan_std_out

    failure_strings = ["unrecognized option", "option requires an argument", "seems to be down",
                       "but does not seem to be running WordPress.", "has not been found", "Scan Aborted"]
    if not any(failure_string in wpscan_std_out for failure_string in failure_strings):
        ret_vals[RETURN_CODE] = 0

    if wpscan_std_err:
        ret_vals[OUTPUT] += wpscan_std_err

    return ret_vals

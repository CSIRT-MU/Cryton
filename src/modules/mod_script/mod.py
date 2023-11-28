#!/usr/bin/python
import json
import subprocess
from schema import Schema, Optional, Or, SchemaError

from cryton_worker.lib.util.module_util import File, OUTPUT, SERIALIZED_OUTPUT, RETURN_CODE


def validate(arguments: dict) -> int:
    """
    Validate input values for the execute function

    :param arguments: Arguments for module execution
    :return: 0 If arguments are valid
    :raises: Schema Exception
    """
    conf_schema = Schema({
        "script_path": File(str),
        "executable": str,
        Optional("script_arguments"): str,
        Optional(SERIALIZED_OUTPUT): bool,
        Optional("timeout"): Or(str, int)
    })

    conf_schema.validate(arguments)

    return 0


def execute(arguments: dict) -> dict:
    """
    This attack module is for executing custom scripts

    :param dict arguments: dictionary of mandatory subdictionary "arguments" and other optional elements
    :return: Module output containing:
            return_code (0-success, 1-fail),
            output (raw output),
            serialized_process_output (output that can be used in other modules)
    """
    ret_vals = {
        RETURN_CODE: -1,
        OUTPUT: "",
        SERIALIZED_OUTPUT: {}
    }

    try:
        validate(arguments)
    except SchemaError as err:
        ret_vals[OUTPUT] = str(err)
        return ret_vals

    file_exec = arguments.get("script_path")
    special_args = arguments.get("script_arguments")
    serialized_output = arguments.get(SERIALIZED_OUTPUT, False)
    timeout = arguments.get("timeout")
    executable = arguments.get("executable")

    if timeout is not None:
        try:
            timeout = int(timeout)
        except ValueError:
            ret_vals[OUTPUT] = "please check your timeout input"
            return ret_vals
    else:
        timeout = None

    cmd = [executable, file_exec]

    if special_args:
        special_args = str(special_args).split(" ")
        for each in special_args:
            cmd.append(str(each))

    try:
        process = subprocess.run(cmd, timeout=timeout, capture_output=True)
        process.check_returncode()
    except subprocess.TimeoutExpired:
        ret_vals[OUTPUT] = "Timeout expired"
        return ret_vals
    except subprocess.CalledProcessError as err:  # process exited with return code other than 0
        ret_vals[OUTPUT] = err.stderr.decode("utf-8")
        return ret_vals
    except Exception as err:
        ret_vals[OUTPUT] = str(err)
        return ret_vals

    process_stdout = process.stdout.decode("utf-8")
    if not (process_error := process.stderr.decode("utf-8")):
        ret_vals[RETURN_CODE] = 0

    module_output = f"STDOUT: {process_stdout} {chr(10)} STDERR: {process_error}"

    ret_vals[OUTPUT] = module_output

    if serialized_output:
        try:
            script_serialized_output = json.loads(process_stdout)
            ret_vals[SERIALIZED_OUTPUT] = script_serialized_output
        except (json.JSONDecodeError, TypeError):
            module_output += "serialized_output_error: Output of the script is not valid JSON."
            ret_vals[RETURN_CODE] = -1

    ret_vals[OUTPUT] = module_output

    return ret_vals

#!/usr/bin/python
import json
import traceback
import subprocess
from typing import Optional, Union
from schema import Schema, Optional as SchemaOptional, SchemaError, Or

from cryton.worker.utility.module_util import Metasploit, OUTPUT, SERIALIZED_OUTPUT, RETURN_CODE


def validate(arguments: dict) -> int:
    """
    Validate input values for the execute function

    :param arguments: Arguments for module execution
    :return: 0 If arguments are valid
    :raises: Schema Exception
    """
    conf_schema = Schema(
        {
            "cmd": str,
            SchemaOptional("end_checks"): list,
            SchemaOptional("timeout"): int,
            SchemaOptional("minimal_execution_time"): int,
            SchemaOptional("session_id"): Or(int, str),
            SchemaOptional(SERIALIZED_OUTPUT): bool,
        },
    )

    conf_schema.validate(arguments)

    return 0


def serialize_output(output: str, from_session: bool = False, used_command: str = "") -> Union[list, dict]:
    """
    Try to serialize the output.
    :param output: String containing a valid JSON
    :param from_session: If the output is from a session
    :param used_command: What command was used to get the output
    :return: Serialized output
    :raise RuntimeError: If the supplied output is not a valid json
    """
    # This is basically just a guessing game when it comes to Windows shells. It will get better with more data to test.
    # Tested cases:
    #   cmd: Powershell -C "whoami | ConvertTo-Json"
    if from_session:
        processed_output = output.replace(used_command, "", 1).rsplit("\r\n\r\n", 1)[0]
    else:
        processed_output = output

    try:
        serialized_output = json.loads(processed_output)
    except (json.JSONDecodeError, TypeError):
        raise TypeError("serialized_output_error: Output of the script is not valid JSON.")

    if isinstance(serialized_output, str):
        serialized_output = {"auto_serialized": serialized_output}

    return serialized_output


def execute(arguments: dict) -> dict:
    """
    Takes arguments in form of dictionary and runs command based on them.

    :param arguments: Arguments from which is compiled and ran command
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

    session_id: Union[int, str, None] = arguments.get("session_id")
    cmd: str = arguments.get("cmd")
    end_checks: Optional[list] = arguments.get("end_checks")
    timeout: Optional[int] = arguments.get("timeout")
    minimal_execution_time: Optional[int] = arguments.get("minimal_execution_time")
    serialized_output: bool = arguments.get(SERIALIZED_OUTPUT, False)

    if session_id is not None:
        if Metasploit().is_connected() is False:
            ret_vals[OUTPUT] = "Could not connect to msfrpc, is msfrpc running?"
            return ret_vals

        try:
            msf = Metasploit()
            process_output = msf.execute_in_session(cmd, str(session_id), timeout, end_checks,
                                                    minimal_execution_time=minimal_execution_time)
        except Exception as ex:
            ret_vals[OUTPUT] = str(ex)
            return ret_vals

        ret_vals.update({RETURN_CODE: 0, OUTPUT: process_output})

    else:
        try:
            process = subprocess.run(cmd, timeout=timeout, capture_output=True, shell=True)
            process.check_returncode()
            process_output = process.stdout.decode("utf-8")
            process_error = process.stderr.decode("utf-8")

        except subprocess.TimeoutExpired:
            ret_vals[OUTPUT] = "Command execution timed out"
            return ret_vals
        except subprocess.CalledProcessError as err:  # exited with return code other than 0
            ret_vals[OUTPUT] = err.stderr.decode("utf-8")
            return ret_vals
        except Exception as ex:
            tb = traceback.format_exc()
            process_output = f"{ex}{chr(10)}{tb}"
            ret_vals[OUTPUT] = process_output
            return ret_vals

        ret_vals[OUTPUT] = f"{process_output}{chr(10)}{process_error}"
        if not process_error:
            ret_vals[RETURN_CODE] = 0

    if serialized_output:
        try:
            ret_vals[SERIALIZED_OUTPUT] = serialize_output(process_output, session_id is not None, cmd)
        except TypeError as ex:
            ret_vals[OUTPUT] += f"{chr(10)}{ex}"
            ret_vals[RETURN_CODE] = -1

    return ret_vals

from typing import Optional as OptionalType, List
import subprocess
import json
from schema import Schema, Optional, Use, SchemaError
import time
import os
import errno


from cryton.worker.utility.module_util import OUTPUT, File, SERIALIZED_OUTPUT, RETURN_CODE

def validate(arguments: dict) -> int:
    """
    Validate input values for the execute function.

    :param arguments: Arguments for module execution
    :return: 0 If arguments are valid
    :raises Schema Exception
    """

    conf_schema = Schema(
        {
            "target": str,
            "wordlist": File(str),
            Optional('options'): str,
            Optional(SERIALIZED_OUTPUT): bool,
        },
    )

    conf_schema.validate(arguments)

    return 0


def parse_command(arguments) -> List[str]:
    serialized_output: bool = arguments.get('serialized_output', True)
    target = arguments.get("target")
    wordlist = arguments.get("wordlist")
    options = arguments.get("options")

    command = ["ffuf"]
    command += ["-w", wordlist, "-u", target]

    # use current timestamp for unique file
    # generic out file is being createed because ffuf doesn't print plain json to console
    time_stamp = time.time()
    global ffuf_tmp_file
    ffuf_tmp_file = "/tmp/cryton-ffuf-" + str(time_stamp) + ".tmp"
    if serialized_output:
        command += ["-of", "json", "-o", ffuf_tmp_file]
    
    if options is not None:
        command += options.split(' ')
    
    return command


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

    ffuf_command = parse_command(arguments)

    try:
        ffuf_run = subprocess.run(ffuf_command, capture_output=True)
    except OSError as err:
        ret_vals[OUTPUT] = f"Original Error: {err}"
        return ret_vals
    except subprocess.SubprocessError as err:
        ret_vals[OUTPUT] = f"ffuf couldn't start. Original Error: {err}"
        return ret_vals

    ffuf_std_out = ffuf_run.stdout.decode('utf-8')
    ffuf_std_err = ffuf_run.stderr.decode('utf-8')


    serialized_output: bool = arguments.get('serialized_output', True)
    if serialized_output == True:
        try:
            with open(ffuf_tmp_file) as f:
                tmp_file_content = f.read()

                try:
                    ret_vals[SERIALIZED_OUTPUT] = json.loads(tmp_file_content)
                except json.JSONDecodeError:
                    ret_vals[OUTPUT] += tmp_file_content
        except OSError as ex:
            ret_vals[OUTPUT] += f"Unable to get the serialized data. Reason: {ex}"

        #delete tmp file
        try:
            os.remove(ffuf_tmp_file)
        except OSError as e:
            pass
 
 
    if "Encountered error" not in ffuf_std_out and "Encountered error" not in ffuf_std_err and ffuf_run.returncode is not None:
        ret_vals[RETURN_CODE] = 0
    
    if ffuf_std_err:
        ret_vals[OUTPUT] += ffuf_std_err
    
    ret_vals[OUTPUT] += ffuf_std_out
    
    return ret_vals


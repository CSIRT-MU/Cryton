import subprocess
from typing import Optional as OptionalType
from schema import Schema, Optional, Or, SchemaError

from cryton_worker.lib.util.module_util import File, OUTPUT, SERIALIZED_OUTPUT, RETURN_CODE


def validate(arguments: dict) -> int:
    """
    Validate input values for the execute function

    :param arguments: Arguments for module execution
    :return: 0 If arguments are valid
    :raises: Schema Exception
    """
    credentials_validation = Or(
        {Optional("username_file"): File(str), Optional("password_file"): File(str)},
        {Optional("username_file"): File(str), Optional("password"): str},
        {Optional("password_file"): File(str), Optional("username"): str},
        {Optional("password"): str, Optional("username"): str},
        only_one=True)

    conf_schema = Schema(Or(
        {
            "command": str,
            Optional("raw_output"): bool,
        },
        {
            "target": str,
            Optional("mod"): str,
            Optional("raw_output"): bool,
            Optional("tasks"): Or(str, int),
            Optional("credentials"): Or(
                {
                    "combo_file": str
                },
                credentials_validation
            )
        }
    ))

    conf_schema.validate(arguments)

    return 0


def parse_username(username: OptionalType[str], username_list: OptionalType[str]) -> list:
    """
    Parse either username or path to file with usernames into medusa command parameter.

    :param username: Username for bruteforce
    :param username_list: Path to file with usernames
    :return: Username parameter for medusa command
    """
    if username is not None:
        return ["-u", username]
    if username_list is not None:
        return ["-U", username_list]
    return []


def parse_password(password: OptionalType[str], password_list: OptionalType[str]) -> list:
    """
    Parse either password or path to file with passwords into medusa command parameter.

    :param password: Password for bruteforce
    :param password_list: Path to file with passwords
    :return: Password parameter for medusa command
    """
    if password is not None:
        return ["-p", password]
    if password_list is not None:
        return ["-P", password_list]
    return []


def parse_credentials(medusa_output: str) -> dict:
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


def parse_command(arguments: dict) -> list:
    target = arguments.get("target")
    mod = arguments.get("mod", "ssh")
    tasks = arguments.get("tasks", 4)
    credentials = arguments.get("credentials")
    username = credentials.get("username")
    username_file = credentials.get("username_file")
    password = credentials.get("password")
    password_file = credentials.get("password_file")
    combo_file = credentials.get("combo_file")

    command = ["medusa", "-h", target, "-t", str(tasks), "-M", mod]

    if combo_file is None:
        command += parse_username(username, username_file) + parse_password(password, password_file)
    else:
        command += ["-C", combo_file]

    return command


def execute(arguments: dict) -> dict:
    """
    Takes arguments in form of dictionary and runs Medusa based on them.

    :param arguments: Arguments from which is compiled and ran medusa command
    :return: Module output containing:
                return_code (0-success, 1-fail, 2-err),
                output (raw output),
                serialized_output (parsed output that can be used in other modules),
    """

    # setting default return values
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

    # parsing input arguments
    std_out_flag = arguments.get("raw_output", False)

    # assembling medusa command
    if "command" in arguments:
        command_input = arguments.get("command")
        command = command_input.split(" ")
    else:
        try:
            command = parse_command(arguments)
        except FileNotFoundError as file_error:
            ret_vals[OUTPUT] = str(file_error)
            return ret_vals

    # executing medusa bruteforce
    try:
        medusa_process = subprocess.run(command, capture_output=True)
    except FileNotFoundError as err:
        ret_vals.update({OUTPUT: f"Check if your command starts with \"medusa\" and is installed. "
                                 f"original error: {err}"})
        return ret_vals
    except subprocess.SubprocessError as err:
        ret_vals[OUTPUT] = f"Medusa couldn\'t start. original error: {err}"
        return ret_vals

    # reporting results
    medusa_stdout = medusa_process.stdout.decode("utf-8")
    medusa_stderr = medusa_process.stderr.decode("utf-8")
    serialized_output = None

    if "ACCOUNT FOUND:" in medusa_stdout and "[SUCCESS]" in medusa_stdout:
        ret_vals[RETURN_CODE] = 0
        serialized_output = parse_credentials(medusa_stdout)

    if std_out_flag:
        ret_vals[OUTPUT] = medusa_stdout + " "

    ret_vals[OUTPUT] += medusa_stderr

    ret_vals[SERIALIZED_OUTPUT] = serialized_output

    return ret_vals

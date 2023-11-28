#!/usr/bin/python
import re
import copy
import sys
import time
import socket

from schema import Schema, Optional as SchemaOptional, Or, SchemaError
from typing import Optional
from pymetasploit3.msfrpc import PayloadModule, MsfError, MsfConsole, MsfRpcError
from cryton_worker.lib.util.module_util import Metasploit, OUTPUT, SERIALIZED_OUTPUT, RETURN_CODE


def validate(arguments: dict) -> int:
    """
    Validate input values for the execute function.
    :param arguments: Arguments for module execution
    :return: 0 If arguments are valid
    :raises: Schema Exception
    """
    arguments_validation = {
        SchemaOptional("session_target"): str,
        "module_type": Or("exploit", "post", "encoder", "auxiliary", "nop", "payload", only_one=True),
        "module": str,
        SchemaOptional("wait_for_result"): bool,
        SchemaOptional("module_retries"): int,
        SchemaOptional("module_timeout"): int,
        SchemaOptional("raw_output"): bool,
        SchemaOptional("module_options"): {SchemaOptional(str): Or(str, int, bool)},
    }

    if arguments.get("module_type") == "exploit":
        arguments_validation[SchemaOptional("payload")] = str
        arguments_validation[SchemaOptional("payload_options")] = {SchemaOptional(str): Or(str, int, bool)}

    conf_schema = Schema(arguments_validation)
    conf_schema.validate(arguments)

    return 0


def create_msf_command(mod, payload: PayloadModule = None, run_as_job=False) -> str:
    """
    Create commands for execution in MSF console.
    :param mod: MSF module object from pymetasploit3
    :param payload: payload module object from pymetasploit3
    :param run_as_job: Flag whether the exploit should be run as a background job
    :return: string of commands to be written into the console
    """
    options_str = f"use {mod.moduletype}/{mod.modulename}\n"
    opts = mod.runoptions
    if payload is None:
        opts["DisablePayloadHandler"] = True

    # Set payload params
    if mod.moduletype == "exploit":
        opts["TARGET"] = mod.target
        if "DisablePayloadHandler" in opts and opts["DisablePayloadHandler"]:
            pass
        elif isinstance(payload, PayloadModule):
            if payload.modulename not in mod.payloads:
                raise ValueError(
                    "Invalid payload ({}) for given target ({}).".format(payload.modulename, mod.target))
            options_str += "set payload {}\n".format(payload.modulename)
            for payload_parameter, payload_value in payload.runoptions.items():
                if payload_value is None or (isinstance(payload_value, str) and not payload_value):
                    continue
                options_str += f"set {payload_parameter} {payload_value}\n"
        else:
            raise ValueError("No valid PayloadModule provided for exploit execution.")

    # Set module params
    for parameter, value in opts.items():
        options_str += f"set {parameter} {value}\n"

    # Run the module without directly opening a command line
    options_str += "run -z"
    if run_as_job:
        options_str += " -j"
    return options_str


def create_last_command_output(options_str: str) -> str:
    """
    Create an output that should be returned by the last `set` command created in create_msf_command().
    This is to ensure the command has actually started
    :param options_str: string of commands to be written into the console
    :return: String to match the last command's output
    """
    last_command = options_str.rsplit("\nrun -z")[0].rsplit("\n", 1)[-1].split()
    return f"{last_command[1]} => {last_command[2]}"


def run_module_with_output(msf_console: MsfConsole, options_str: str, module_timeout: int) -> str:
    """
    Execute a module and wait for the returned output.
    :param msf_console: MsfConsole object from pymetasploit3
    :param options_str: string of commands to be written into the console
    :param module_timeout: number of seconds for which should function try to read output from console
    :return: Output from a console
    """
    if msf_console.is_busy():
        for _ in range(6):
            time.sleep(1)
            if not msf_console.is_busy():
                break
        else:
            raise MsfError(f"Console {msf_console.cid} is busy")

    msf_console.read()  # clear console_output buffer
    msf_console.write(options_str)

    console_output = ""
    module_timeout += time.time()
    last_command_output = create_last_command_output(options_str)
    while console_output == "" or () or msf_console.is_busy() or last_command_output not in console_output:
        time.sleep(1)
        console_output += msf_console.read()["data"]
        if time.time() >= module_timeout:
            break

    return console_output


def get_created_session(msf: Metasploit, session_target: str, exploit_name: str, payload_name: str,
                        before_sessions: list) -> Optional[str]:
    """
    Check newly created sessions to session_target.
    :param msf: Metasploit object
    :param session_target: Target IP address
    :param exploit_name: Name of a msf module
    :param payload_name: Name of a msf payload
    :param before_sessions: Msf sessions before module execution
    :return: Bool value telling if the new session was created
    """
    # get sessions after
    after_sessions = msf.get_sessions(target_host=session_target, via_exploit=exploit_name, via_payload=payload_name)

    # Get new session
    new_sessions_to_same_host = list(set(after_sessions) - set(before_sessions))

    if len(new_sessions_to_same_host) > 0:
        return new_sessions_to_same_host[-1]
    return None


def get_session_target(module_options: dict) -> Optional[str]:
    """
    Try to find and parse target's IPv4 address.
    :param module_options: MSF module options
    :return: Target's IPv4 address
    """
    for module_option in module_options:
        if re.match(r"^rhosts?$", module_option, re.IGNORECASE):
            for possible_target in module_options.get(module_option).split():
                try:  # Check if the input is IPv4
                    socket.inet_aton(possible_target)
                    return possible_target
                except OSError:
                    pass

                try:  # Check if the input is domain and try to translate it
                    return socket.gethostbyname(possible_target)
                except socket.gaierror:
                    pass


def execute(args: dict) -> dict:
    """
    Takes arguments in form of dictionary and runs Msf based on them.
    :param args: Arguments from which is compiled and ran medusa command
    :return: Module output containing:
                return_code (0-success, -1-fail),
                output (raw output),
                serialized_output (parsed output that can be used in other modules),

    """
    ret_vals = {
        RETURN_CODE: -1,
        OUTPUT: "",
        SERIALIZED_OUTPUT: {}
    }

    try:
        validate(args)
    except SchemaError as err:
        ret_vals[OUTPUT] = str(err)
        return ret_vals

    # Copy arguments to not change them by mistake
    arguments = copy.deepcopy(args)

    # Parse exploit
    session_target: str = arguments.get("session_target")
    module_type: str = arguments.get("module_type")
    module: str = arguments.get("module")
    payload: str = arguments.get("payload", "")
    std_out_flag: bool = arguments.get("raw_output", True)
    module_options: dict = arguments.get("module_options")
    payload_options: dict = arguments.get("payload_options")
    wait_for_result: bool = arguments.get("wait_for_result", True)
    module_timeout: int = arguments.get("module_timeout", 300)
    module_retries: int = arguments.get("module_retries", 1)
    run_as_job = not wait_for_result

    if module_type in module:
        module = module.replace(f"{module_type}/", "")

    # Check connection to msfrpc
    if Metasploit().is_connected() is False:
        ret_vals[OUTPUT] = "Could not connect to msfrpc, is msfrpc running?"
        return ret_vals

    # Open client
    try:
        msf = Metasploit()
    except Exception:
        ret_vals[OUTPUT] = str(sys.exc_info())
        return ret_vals

    # Try to parse session_target from module options. Returns the first found host
    if session_target is None:
        session_target = get_session_target(module_options)

    if session_target is not None:
        # Get sessions before
        before_sessions = msf.get_sessions(target_host=session_target, via_exploit=module, via_payload=payload)

    # create msf_module and payload objects
    payload_object = None
    try:
        msf_module_object = msf.client.modules.use(module_type, module)
        if module_options:
            for option, value in module_options.items():
                try:
                    msf_module_object.update({option: value})
                except TypeError:  # TODO: hotfix for int/str session conversion problems
                    if value.isdigit():
                        msf_module_object.update({option: int(value)})

        if payload != "" and module_type == "exploit":
            # only for exploit type module
            payload_object = msf.client.modules.use("payload", payload)
            if payload_options:
                payload_object.update(payload_options)

        msf_command = create_msf_command(msf_module_object, payload_object, run_as_job)
    except (KeyError, ValueError, TypeError, MsfRpcError) as err:
        ret_vals[OUTPUT] = str(err)
        return ret_vals

    all_console_outputs = ""
    output_from_console = ""
    exploit_runs = 0
    while exploit_runs < module_retries:
        msf_console = msf.client.consoles.console()  # Create a msf console
        output_from_console = run_module_with_output(msf_console, msf_command, module_timeout)
        all_console_outputs += f"{output_from_console}\n"
        # String check is a hotfix for exploits that don't succeed on the first try
        if output_from_console and "Exploit completed, but no session was created." not in output_from_console:
            break
        exploit_runs += 1
        msf_console.destroy()
        ret_vals[OUTPUT] += f"MSF module did not finish successfully on attempt number: {exploit_runs}\n"

    if exploit_runs >= module_retries:
        ret_vals[OUTPUT] += f"Could not successfully finish within the given number of attempts.\n"

    # Return output
    if std_out_flag is True:
        ret_vals[OUTPUT] += all_console_outputs

    # TODO: maybe not accurate for all modules/exploits, needs further testing
    if 'Success' in output_from_console or 'Command shell session' in output_from_console or 'Meterpreter session' \
            in output_from_console or "Upgrading session ID:" in output_from_console or \
            "Command Stager progress - 100.00%" in output_from_console or '[+]' in output_from_console or \
            "Starting the SOCKS proxy server" in output_from_console:
        ret_vals[RETURN_CODE] = 0

    # Check for Error or Success
    if session_target is not None:
        new_session_id = get_created_session(msf, session_target, module, payload, before_sessions)
        if new_session_id is not None:
            ret_vals[RETURN_CODE] = 0
            ret_vals[SERIALIZED_OUTPUT] = {"session_id": new_session_id}

    return ret_vals

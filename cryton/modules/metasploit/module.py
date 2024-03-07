import re
import sys
import time
import socket
from typing import Optional
from pymetasploit3.msfrpc import PayloadModule, MsfError, MsfConsole, MsfRpcError

from cryton.worker.utility.util import Metasploit
from cryton.lib.utility.module import ModuleBase, ModuleOutput, Result


# TODO: this module is only updated to work with the new rules, it's not reworked
#  - update validation (mainly descriptions)
#  - update check_requirements
#  - rework the module
#  - add tests
class Module(ModuleBase):
    SCHEMA = {
        "type": "object",
        "description": "Arguments for the `metasploit` module.",
        "properties": {
            "session_filter": {
                "type": "object",
                "description": "",
                "properties": {
                    "type": {"type": "string"},
                    "tunnel_local": {"type": "string"},
                    "tunnel_peer": {"type": "string"},
                    "via_exploit": {"type": "string"},
                    "via_payload": {"type": "string"},
                    "desc": {"type": "string"},
                    "info": {"type": "string"},
                    "workspace": {"type": "string"},
                    "session_host": {"type": "string"},
                    "session_port": {"type": "integer"},
                    "target_host": {"type": "string"},
                    "username": {"type": "string"},
                    "uuid": {"type": "string"},
                    "exploit_uuid": {"type": "string"},
                    "routes": {"type": "string"},
                    "arch": {"type": "string"},
                    "platform": {"type": "string"}
                },
                "additionalProperties": False
            },
            "ignore_old_sessions": {"type": "boolean", "description": ""},
            "module_type": {
                "type": "string",
                "enum": ["exploit", "post", "encoder", "auxiliary", "nop", "payload"],
                "description": ""
            },
            "module": {"type": "string", "description": ""},
            "wait_for_result": {"type": "boolean", "description": ""},
            "module_retries": {"type": "integer", "description": ""},
            "module_timeout": {"type": "integer", "description": ""},
            "module_options": {"type": "object", "description": ""},
            "if": {
                "properties": {
                    "module_type": {"const": "exploit"}
                }
            },
            "then": {
                "properties": {
                    "payload": {"type": "string", "description": ""},
                    "payload_options": {"type": "object", "description": ""}
                },
                "additionalProperties": False
            },
            # "additionalProperties": False  # TODO: solve
        },
        "required": ["module_type", "module"]
    }

    def __init__(self, arguments: dict):
        super().__init__(arguments)

    def check_requirements(self) -> None:
        pass

    def execute(self) -> ModuleOutput:
        # Parse exploit
        session_filter: dict = self._arguments.get("session_filter")
        ignore_old_sessions: bool = self._arguments.get("ignore_old_sessions", True)
        module_type: str = self._arguments.get("module_type")
        module: str = self._arguments.get("module")
        payload: str = self._arguments.get("payload", "")
        std_out_flag: bool = self._arguments.get("raw_output", True)
        module_options: dict = self._arguments.get("module_options")
        payload_options: dict = self._arguments.get("payload_options")
        wait_for_result: bool = self._arguments.get("wait_for_result", True)
        module_timeout: int = self._arguments.get("module_timeout", 300)
        module_retries: int = self._arguments.get("module_retries", 1)
        run_as_job = not wait_for_result

        if module_type in module:
            module = module.replace(f"{module_type}/", "")

        # Check connection to msfrpc
        if Metasploit().is_connected() is False:
            self._data.output = "Could not connect to msfrpc, is msfrpc running?"
            return self._data

        # Open client
        try:
            msf = Metasploit()
        except Exception:
            self._data.output = str(sys.exc_info())
            return self._data

        if session_filter is None and (session_target := get_session_target(module_options)) is not None:
            session_filter = {"target_host": session_target, "via_exploit": module, "via_payload": payload}

        ignored_sessions = [] if session_filter is None or not ignore_old_sessions else msf.get_sessions()

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
            self._data.output = str(err)
            return self._data

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
            self._data.output += f"MSF module did not finish successfully on attempt number: {exploit_runs}\n"

        if exploit_runs >= module_retries:
            self._data.output += f"Could not successfully finish within the given number of attempts.\n"

        # Return output
        if std_out_flag is True:
            self._data.output += all_console_outputs

        # TODO: maybe not accurate for all modules/exploits, needs further testing
        if 'Success' in output_from_console or 'Command shell session' in output_from_console or 'Meterpreter session' \
                in output_from_console or "Upgrading session ID:" in output_from_console or \
                "Command Stager progress - 100.00%" in output_from_console or '[+]' in output_from_console or \
                "Starting the SOCKS proxy server" in output_from_console:
            self._data.result = Result.OK

        # Check for Error or Success
        if session_filter is not None:
            new_session_id = get_created_session(msf, ignored_sessions, **session_filter)
            if new_session_id is not None:
                self._data.result = Result.OK
                self._data.serialized_output = {"session_id": new_session_id}
        return self._data


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


def get_created_session(msf: Metasploit, ignored_sessions: list[int], **kwargs) -> Optional[int]:
    """
    Check newly created sessions and filter them.
    :param msf: Metasploit object
    :param ignored_sessions: Msf sessions to be filtered
    :return: Bool value telling if the new session was created
    """
    sessions = msf.get_sessions(**kwargs)
    new_sessions = list(set(sessions) - set(ignored_sessions))

    if len(new_sessions) > 0:
        return new_sessions[-1]
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

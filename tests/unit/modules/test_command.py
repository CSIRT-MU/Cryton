import subprocess
from unittest.mock import Mock
from pytest_mock import MockerFixture
import pytest

from cryton.modules.command.module import Module, Result
from snek_sploit import Error as MSFError


class TestModuleCommand:
    path = "cryton.modules.command.module"

    @pytest.fixture
    def f_metasploit(self, mocker: MockerFixture):
        return mocker.patch(f"{self.path}.MetasploitClientUpdated")

    @pytest.fixture
    def f_subprocess_run(self, mocker: MockerFixture):
        return mocker.patch(f"{self.path}.subprocess.run")

    @pytest.mark.parametrize(
        "p_arguments",
        [
            {"command": "placeholder"},
            {
                "command": "placeholder",
                "end_checks": ["placeholder"],
                "timeout": 1,
                "minimal_execution_time": 1,
                "serialize_output": True,
                "session_id": 1,
                "force_shell": True,
            },
        ]
    )
    def test_schema(self, p_arguments: dict):
        Module.validate_arguments(p_arguments)

    @pytest.mark.parametrize(
        "p_arguments",
        [
            {},
            {"non_existent": "placeholder"},
            {"command": "placeholder", "non_existent": "placeholder"}
        ]
    )
    def test_schema_error(self, p_arguments: dict):
        with pytest.raises(Exception):
            Module.validate_arguments(p_arguments)

    def test_init(self):
        arguments = {
            "command": "placeholder",
            "end_checks": ["placeholder"],
            "timeout": 1,
            "minimal_execution_time": 1,
            "serialize_output": True,
            "session_id": 1,
            "force_shell": False
        }
        module = Module(arguments)

        assert module._command == arguments.get("command")
        assert module._end_checks == arguments.get("end_checks")
        assert module._timeout == arguments.get("timeout")
        assert module._minimal_execution_time == arguments.get("minimal_execution_time")
        assert module._serialize_output_flag == arguments.get("serialize_output")
        assert module._session_id == arguments.get("session_id")
        assert module._force_shell == arguments.get("force_shell")

    def test_check_requirements_no_session(self, f_metasploit):
        assert Module({"command": "placeholder"}).check_requirements() is None

    def test_check_requirements_no_msf_connection(self, f_metasploit):
        f_metasploit.return_value.health.rpc.check.side_effect = [ConnectionError]

        module = Module({"command": "placeholder", "session_id": 1})

        with pytest.raises(ConnectionError):
            module.check_requirements()

    def test_check_requirements_wrong_msf_credentials(self, f_metasploit):
        f_metasploit.return_value.login.side_effect = [MSFError]

        module = Module({"command": "placeholder", "session_id": 1})

        with pytest.raises(RuntimeError):
            module.check_requirements()

    def test_execute(self, f_subprocess_run):
        module = Module({"command": "placeholder", "serialize_output": True})

        f_subprocess_run.return_value.stdout = b"placeholder"
        f_subprocess_run.return_value.stderr = b""

        module._serialize_output = Mock(return_value={"example": "example"})

        result = module.execute()

        assert result.result == Result.OK
        assert result.output == "placeholder\n"
        assert result.serialized_output == {"example": "example"}

    def test_execute_process_timeout(self, f_subprocess_run):
        module = Module({"command": "placeholder", "serialize_output": True})

        f_subprocess_run.side_effect = subprocess.TimeoutExpired("", 1)

        result = module.execute()

        assert result.result == Result.FAIL
        assert result.output == "Command execution timed out."
        assert result.serialized_output == {}

    def test_execute_process_error(self, f_subprocess_run):
        module = Module({"command": "placeholder", "serialize_output": True})

        f_subprocess_run.side_effect = subprocess.CalledProcessError(1, "", stderr=b"error")

        result = module.execute()

        assert result.result == Result.FAIL
        assert result.output == "error"
        assert result.serialized_output == {}

    def test_execute_error(self, f_subprocess_run):
        module = Module({"command": "placeholder", "serialize_output": True})

        f_subprocess_run.side_effect = Exception("error")

        result = module.execute()

        assert result.result == Result.FAIL
        assert result.output == "error"
        assert result.serialized_output == {}

    def test_execute_serialization_error(self, f_subprocess_run):
        module = Module({"command": "placeholder", "serialize_output": True})

        f_subprocess_run.return_value.stdout = b"output"
        f_subprocess_run.return_value.stderr = b""

        module._serialize_output = Mock(side_effect=TypeError("error"))

        result = module.execute()

        assert result.result == Result.FAIL
        assert result.output == "output\n\nerror"
        assert result.serialized_output == {}

    def test_execute_session(self, f_metasploit):
        module = Module({"command": "placeholder", "session_id": 1})

        mock_session = Mock()
        mock_session.execute.return_value = "output"
        f_metasploit.return_value.sessions.get.return_value = mock_session

        result = module.execute()
    
        assert result.result == Result.OK
        assert result.output == "output"
        assert result.serialized_output == {}

    def test_execute_session_error(self, f_metasploit):
        module = Module({"command": "placeholder", "session_id": 1})

        mock_session = Mock()
        mock_session.execute.side_effect = Exception("error")
        f_metasploit.return_value.sessions.get.return_value = mock_session

        result = module.execute()

        assert result.result == Result.FAIL
        assert result.output == "error"
        assert result.serialized_output == {}

    def test_serialize_output(self):
        module = Module({"command": "placeholder"})

        result = module._serialize_output('"output"')

        assert result == {"auto_serialized": "output"}

    def test_serialize_output_session(self):
        module = Module({"command": "placeholder", "session_id": 1})

        result = module._serialize_output('placeholder "output"')

        assert result == {"auto_serialized": "output"}

    def test_serialize_output_error(self):
        module = Module({"command": "placeholder"})

        with pytest.raises(TypeError):
            module._serialize_output('output')

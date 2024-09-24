import subprocess
from unittest.mock import Mock
from pytest_mock import MockerFixture
import pytest

from cryton.modules.medusa.module import Module, Result


class TestModuleMedusa:
    path = "cryton.modules.medusa.module"

    @pytest.fixture
    def f_subprocess_run(self, mocker: MockerFixture):
        return mocker.patch(f"{self.path}.subprocess.run")

    @pytest.fixture
    def f_is_file(self, mocker: MockerFixture):
        return mocker.patch(f"{self.path}.os.path.isfile")

    @pytest.mark.parametrize(
        "p_arguments",
        [
            {
                "target": "placeholder",
                "mod": "placeholder",
                "tasks": 1,
                "options": "placeholder",
                "credentials": {"combo_file": "test"},
            },
            {"target": "placeholder", "credentials": {"username": "test", "password": "test"}},
            {"target": "placeholder", "credentials": {"username": "test", "password_file": "test"}},
            {"target": "placeholder", "credentials": {"username_file": "test", "password": "test"}},
            {"target": "placeholder", "credentials": {"username_file": "test", "password_file": "test"}},
        ],
    )
    def test_schema(self, p_arguments: dict):
        Module.validate_arguments(p_arguments)

    @pytest.mark.parametrize("p_arguments", [{"command": "placeholder"}])
    def test_schema_custom(self, p_arguments: dict):
        Module.validate_arguments(p_arguments)

    @pytest.mark.parametrize(
        "p_arguments",
        [
            {},
            {"non_existent": "placeholder"},
            {"command": "placeholder", "non_existent": "placeholder"},
            {"target": "placeholder"},
            {"credentials": {"combo_file": "test"}},
            {"target": "placeholder", "credentials": {"combo_file": "test"}, "non_existent": "placeholder"},
            {"target": "placeholder", "credentials": {"combo_file": "test"}, "command": "placeholder"},
            {"target": "placeholder", "credentials": {"combo_file": "test", "username": "test"}},
            {"target": "placeholder", "credentials": {"combo_file": "test", "username_file": "test"}},
            {"target": "placeholder", "credentials": {"combo_file": "test", "password": "test"}},
            {"target": "placeholder", "credentials": {"combo_file": "test", "password_file": "test"}},
            {"target": "placeholder", "credentials": {"username": "test", "password": "test", "password_file": "test"}},
        ],
    )
    def test_schema_error(self, p_arguments: dict):
        with pytest.raises(Exception):
            Module.validate_arguments(p_arguments)

    def test_init(self):
        arguments = {
            "target": "placeholder",
            "mod": "placeholder",
            "tasks": 1,
            "options": "placeholder",
            "credentials": {"combo_file": "test"},
            "command": "placeholder",
        }

        module = Module(arguments)

        assert module._target == arguments.get("target")
        assert module._mod == arguments.get("mod")
        assert module._tasks == arguments.get("tasks")
        assert module._options == arguments.get("options")
        assert module._credentials == arguments.get("credentials")
        assert module._command == arguments.get("command")

    @pytest.mark.parametrize(
        "p_arguments",
        [
            {"credentials": {"combo_file": "test"}},
            {"credentials": {"username_file": "test"}},
            {"credentials": {"password_file": "test"}},
        ],
    )
    def test_check_requirements_files(self, p_arguments, f_is_file):
        module = Module(p_arguments)

        f_is_file.return_value = False

        with pytest.raises(OSError):
            module.check_requirements()

    def test_check_requirements_executable(self, f_subprocess_run, f_is_file):
        module = Module({"credentials": {}})

        f_is_file.return_value = True
        f_subprocess_run.side_effect = FileNotFoundError

        with pytest.raises(OSError):
            module.check_requirements()

    def test_check_requirements_command(self):
        module = Module({"command": "placeholder"})

        assert module.check_requirements() is None

    def test_execute(self, f_subprocess_run):
        module = Module({"target": "placeholder"})
        mock_build_command = Mock(return_value="placeholder")
        module._build_command = mock_build_command

        mock_parse_credentials = Mock(return_value={"example": "example"})
        module._parse_credentials = mock_parse_credentials

        f_subprocess_run.return_value.stdout = b"ACCOUNT FOUND: [SUCCESS]"
        f_subprocess_run.return_value.stderr = b""

        result = module.execute()

        assert result.result == Result.OK
        assert result.output == "ACCOUNT FOUND: [SUCCESS]\n"
        assert result.serialized_output == {"example": "example"}
        mock_build_command.assert_called_once()

    def test_execute_process_error(self, f_subprocess_run):
        module = Module({"target": "placeholder"})
        module._build_command = Mock(return_value="placeholder")

        f_subprocess_run.side_effect = subprocess.CalledProcessError(1, "", b"a", b"error")

        result = module.execute()

        assert result.result == Result.FAIL
        assert result.output == "a\nerror"
        assert result.serialized_output == {}

    def test_execute_error(self, f_subprocess_run):
        module = Module({"target": "placeholder"})
        module._build_command = Mock(return_value="placeholder")

        f_subprocess_run.side_effect = Exception("error")

        result = module.execute()

        assert result.result == Result.FAIL
        assert result.output == "error"
        assert result.serialized_output == {}

    def test_execute_command(self, f_subprocess_run):
        module = Module({"command": "placeholder"})
        mock_build_command = Mock()
        module._build_command = mock_build_command

        mock_parse_credentials = Mock(return_value={"example": "example"})
        module._parse_credentials = mock_parse_credentials

        f_subprocess_run.return_value.stdout = b"ACCOUNT FOUND: [SUCCESS]"
        f_subprocess_run.return_value.stderr = b""

        result = module.execute()

        assert result.result == Result.OK
        assert result.output == "ACCOUNT FOUND: [SUCCESS]\n"
        assert result.serialized_output == {"example": "example"}
        mock_build_command.assert_not_called()

    @pytest.mark.parametrize(
        "p_arguments, p_outcome",
        [
            (
                {"target": "placeholder", "options": "a b", "credentials": {"combo_file": "test"}},
                ["medusa", "-h", "placeholder", "-t", "4", "-M", "ssh", "-C", "test", "a", "b"],
            ),
            (
                {"target": "placeholder", "credentials": {"username": "test", "password": "test"}},
                ["medusa", "-h", "placeholder", "-t", "4", "-M", "ssh", "-u", "test", "-p", "test"],
            ),
            (
                {"target": "placeholder", "credentials": {"username": "test", "password_file": "test"}},
                ["medusa", "-h", "placeholder", "-t", "4", "-M", "ssh", "-u", "test", "-P", "test"],
            ),
            (
                {"target": "placeholder", "credentials": {"username_file": "test", "password": "test"}},
                ["medusa", "-h", "placeholder", "-t", "4", "-M", "ssh", "-U", "test", "-p", "test"],
            ),
            (
                {"target": "placeholder", "credentials": {"username_file": "test", "password_file": "test"}},
                ["medusa", "-h", "placeholder", "-t", "4", "-M", "ssh", "-U", "test", "-P", "test"],
            ),
        ],
    )
    def test__build_command(self, p_arguments, p_outcome):
        module = Module(p_arguments)

        result = module._build_command()

        assert result == p_outcome

    def test_parse_credentials(self):
        result = Module._parse_credentials(
            "ACCOUNT FOUND: [ssh] Host: address User: username Password: password [SUCCESS]"
        )

        assert result == {
            "username": "username",
            "password": "password",
            "all_credentials": [{"username": "username", "password": "password"}],
        }

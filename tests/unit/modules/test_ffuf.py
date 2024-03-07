import json
import subprocess
from unittest.mock import Mock, mock_open
from pytest_mock import MockerFixture
import pytest

from cryton.modules.ffuf.module import Module, Result


class TestModuleFFUF:
    path = "cryton.modules.ffuf.module"

    @pytest.fixture
    def f_subprocess_run(self, mocker: MockerFixture):
        return mocker.patch(f"{self.path}.subprocess.run")

    @pytest.fixture
    def f_is_file(self, mocker: MockerFixture):
        return mocker.patch(f"{self.path}.os.path.isfile")

    @pytest.fixture
    def f_uuid1(self, mocker: MockerFixture):
        return mocker.patch(f"{self.path}.uuid1")

    @pytest.fixture
    def f_json_load(self, mocker: MockerFixture):
        return mocker.patch(f"{self.path}.json.load")

    @pytest.fixture
    def f_open(self, mocker: MockerFixture):
        return mocker.patch(f"builtins.open", mock_open())

    @pytest.fixture
    def f_os_remove(self, mocker: MockerFixture):
        return mocker.patch(f"{self.path}.os.remove")

    @pytest.mark.parametrize(
        "p_arguments",
        [
            {"target": "placeholder", "wordlist": "placeholder"},
            {"target": "placeholder", "wordlist": "placeholder", "options": "a b c", "serialize_output": True},
        ]
    )
    def test_schema(self, p_arguments: dict):
        Module.validate_arguments(p_arguments)

    @pytest.mark.parametrize(
        "p_arguments",
        [
            {"command": "placeholder"}
        ]
    )
    def test_schema_custom(self, p_arguments: dict):
        Module.validate_arguments(p_arguments)

    @pytest.mark.parametrize(
        "p_arguments",
        [
            {},
            {"non_existent": "placeholder"},
            {"command": "placeholder", "non_existent": "placeholder"},
            {"target": "placeholder"},
            {"wordlist": "placeholder"},
            {"target": "placeholder", "wordlist": "placeholder", "non_existent": "placeholder"},
            {"target": "placeholder", "wordlist": "placeholder", "command": "placeholder"}
        ]
    )
    def test_schema_error(self, p_arguments: dict):
        with pytest.raises(Exception):
            Module.validate_arguments(p_arguments)

    def test_init(self, f_uuid1):
        arguments = {
            "command": "placeholder",
            "target": "placeholder",
            "wordlist": "placeholder",
            "options": "placeholder",
            "serialize_output": True,
        }

        f_uuid1.return_value = "uuid"

        module = Module(arguments)

        assert module._command == arguments.get("command")
        assert module._target == arguments.get("target")
        assert module._wordlist == arguments.get("wordlist")
        assert module._options == arguments.get("options")
        assert module._serialize_output == arguments.get("serialize_output")
        assert module._tmp_file == "/tmp/cryton-report-ffuf-uuid"

    def test_check_requirements_wordlist(self, f_subprocess_run, f_is_file):
        module = Module({"target": "placeholder", "wordlist": "placeholder"})

        f_is_file.return_value = False

        with pytest.raises(OSError):
            module.check_requirements()

    def test_check_requirements_executable(self, f_subprocess_run, f_is_file):
        module = Module({"target": "placeholder", "wordlist": "placeholder"})

        f_is_file.return_value = True
        f_subprocess_run.side_effect = FileNotFoundError

        with pytest.raises(OSError):
            module.check_requirements()

    def test_check_requirements_command(self):
        module = Module({"command": "placeholder"})

        assert module.check_requirements() is None

    def test_execute(self, f_subprocess_run, f_open, f_json_load, f_is_file, f_os_remove):
        module = Module({"target": "placeholder", "wordlist": "placeholder"})
        mock_build_command = Mock()
        module._build_command = mock_build_command

        f_json_load.return_value = {"example": "example"}
        f_subprocess_run.return_value.stdout = b"placeholder"
        f_subprocess_run.return_value.stderr = b""
        f_is_file.return_value = True
        f_os_remove.side_effect = OSError

        result = module.execute()

        assert result.result == Result.OK
        assert result.output == "placeholder\n"
        assert result.serialized_output == {"example": "example"}
        mock_build_command.assert_called_once()
        f_os_remove.assert_called_once_with(module._tmp_file)

    def test_execute_process_error(self, f_subprocess_run):
        module = Module({"target": "placeholder", "wordlist": "placeholder"})
        module._build_command = Mock()

        f_subprocess_run.side_effect = subprocess.CalledProcessError(1, "", b"", b"error")

        result = module.execute()

        assert result.result == Result.FAIL
        assert result.output == "\nerror"
        assert result.serialized_output == {}

    def test_execute_error(self, f_subprocess_run):
        module = Module({"target": "placeholder", "wordlist": "placeholder"})
        module._build_command = Mock()

        f_subprocess_run.side_effect = Exception("error")

        result = module.execute()

        assert result.result == Result.FAIL
        assert result.output == "error"
        assert result.serialized_output == {}

    def test_execute_tmp_file_load_error(self, f_subprocess_run, f_open, f_json_load, f_is_file):
        module = Module({"target": "placeholder", "wordlist": "placeholder"})
        module._build_command = Mock()

        f_open.side_effect = OSError("error")
        f_subprocess_run.return_value.stdout = b"placeholder"
        f_subprocess_run.return_value.stderr = b""
        f_is_file.return_value = True

        result = module.execute()

        assert result.result == Result.FAIL
        assert result.output == "placeholder\nUnable to get the serialized data. Reason: error"
        assert result.serialized_output == {}

    def test_execute_tmp_file_load_json_error(self, f_subprocess_run, f_open, f_json_load, f_is_file):
        module = Module({"target": "placeholder", "wordlist": "placeholder"})
        module._build_command = Mock()

        f_json_load.side_effect = json.JSONDecodeError("error", "", 1)
        f_subprocess_run.return_value.stdout = b"placeholder"
        f_subprocess_run.return_value.stderr = b""
        f_is_file.return_value = True

        result = module.execute()

        assert result.result == Result.FAIL
        assert "placeholder\nUnable to get the serialized data. Reason: error" in result.output
        assert result.serialized_output == {}

    def test_execute_command(self, f_subprocess_run, f_is_file):
        module = Module({"command": "placeholder"})
        mock_build_command = Mock()
        module._build_command = mock_build_command

        f_subprocess_run.return_value.stdout = b"placeholder"
        f_subprocess_run.return_value.stderr = b""
        f_is_file.return_value = False

        result = module.execute()

        assert result.result == Result.OK
        assert result.output == "placeholder\n"
        assert result.serialized_output == {}
        mock_build_command.assert_not_called()

    def test__build_command(self):
        module = Module({"target": "placeholder", "wordlist": "placeholder", "options": "a b"})
        module._tmp_file = "test"

        result = module._build_command()

        assert result == ["ffuf", "-w", "placeholder", "-u", "placeholder", "-of", "json", "-o", "test", "a", "b"]

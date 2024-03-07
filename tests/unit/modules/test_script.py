from unittest.mock import patch
from pytest_mock import MockerFixture
import pytest
from dataclasses import asdict

from cryton.modules.script.module import Module, Result


class TestModuleScript:
    path = "cryton.modules.script.module"

    @pytest.mark.parametrize(
        "p_arguments",
        [
            {
                "script_path": "example",
                "executable": "example",
                "script_arguments": "example",
                "serialize_output": True,
                "timeout": 1
            },
            {
                "script_path": "example",
                "executable": "example",
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
            {"script_path": "placeholder"},
            {"executable": "placeholder"},
        ]
    )
    def test_schema_error(self, p_arguments: dict):
        with pytest.raises(Exception):
            Module.validate_arguments(p_arguments)

    def test_check_requirements_command(self):
        module = Module({})

        assert module.check_requirements() is None

    @pytest.mark.parametrize(
        "p_error, p_return_code",
        [
            ("test_error", Result.FAIL),
            ("", Result.OK)
        ]
    )
    def test_execute(self, mocker: MockerFixture, p_error, p_return_code):
        mod_arguments = {
            "script_path": "/tmp/test.py",
            "executable": "python3",
            "serialize_output": True,
            "timeout": 30,
        }
        mocker.patch("os.path.exists", return_value=True)
        completed_process_mock = mocker.patch("subprocess.CompletedProcess")
        completed_process_mock.stdout.decode.return_value = '{"test": "output"}'
        completed_process_mock.stderr.decode.return_value = p_error
        mocker.patch("subprocess.run", return_value=completed_process_mock)

        result = Module(mod_arguments).execute()
        completed_process_mock.check_returncode.assert_called_once()
        assert asdict(result) == {
            "output": '{"test": "output"}\n' + p_error,
            "serialized_output": {"test": "output"},
            "result": p_return_code
        }

        with patch("json.loads", side_effect=TypeError):
            result = Module(mod_arguments).execute()
            assert asdict(result) == {
                "output": "{\"test\": \"output\"}\n" + p_error +
                          "serialized_output_error: Output of the script is not valid JSON.",
                "serialized_output": {},
                "result": Result.FAIL
            }

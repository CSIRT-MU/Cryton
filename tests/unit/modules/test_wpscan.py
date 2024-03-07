from unittest.mock import Mock
import pytest
import subprocess

from cryton.modules.wpscan.module import Module, ModuleOutput, Result, parse_command


class TestModuleWPScan:
    path = "cryton.modules.wpscan.module"

    @pytest.mark.parametrize(
        "p_arguments",
        [
            {
                "target": "example",
                "options": "example",
                "api_token": "example",
                "serialize_output": True,
            },
            {
                "target": "example",
            },
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
            {"target": "placeholder", "command": "placeholder"},
            {"options": "placeholder"},
        ]
    )
    def test_schema_error(self, p_arguments: dict):
        with pytest.raises(Exception):
            Module.validate_arguments(p_arguments)

    def test_check_requirements_command(self):
        module = Module({})

        assert module.check_requirements() is None

    @pytest.mark.parametrize(
        "p_arguments, p_command",
        [
            ({"target": "http://address/index.php", "options": "--request-timeout 60"},
             ['wpscan', '--url', 'http://address/index.php', '-f', 'json', '--request-timeout', '60']),
            ({"command": "test command"}, ["test", "command"]),
        ]
    )
    def test_parse_command(self, p_arguments, p_command):
        command = parse_command(p_arguments)
        assert command == p_command

    @pytest.mark.parametrize(
        "p_stdout, p_stderr, p_final_output",
        [
            ("test_output", "", "test_output"),
            ("test_output\n", "test_error", "test_output\ntest_error"),
        ]
    )
    def test_execute_with_standard_output(self, mocker, p_stdout, p_stderr, p_final_output):
        module_arguments = {"test": "argument"}
        mocker.patch(f"{self.path}.parse_command", return_value=["test", "command"])
        completed_process_mock = mocker.patch("subprocess.CompletedProcess")
        completed_process_mock.stdout.decode.return_value = p_stdout
        completed_process_mock.stderr.decode.return_value = p_stderr
        process_mock = mocker.patch("subprocess.run")
        process_mock.return_value = completed_process_mock

        result = Module(module_arguments).execute()

        process_mock.assert_called_once_with(["test", "command"], capture_output=True)
        assert result == ModuleOutput(Result.OK, p_final_output, {})

    def test_execute_with_json_output(self, mocker):
        module_arguments = {"test": "argument"}
        mocker.patch(f"{self.path}.parse_command", return_value=["test", "command"])
        completed_process_mock = mocker.patch("subprocess.CompletedProcess")
        completed_process_mock.stdout.decode.return_value = '{"test": "output"}'
        completed_process_mock.stderr.decode.return_value = "test_error"
        process_mock = mocker.patch("subprocess.run")
        process_mock.return_value = completed_process_mock

        result = Module(module_arguments).execute()

        process_mock.assert_called_once_with(["test", "command"], capture_output=True)
        assert result == ModuleOutput(Result.OK, "test_error", {"test": "output"})

    @pytest.mark.parametrize(
        "p_exception, p_result",
        [
            (OSError("test_error"), "Check if your command starts with 'wpscan'. Original error: test_error"),
            (subprocess.SubprocessError("test_error"), "WPScan couldn't start. Original error: test_error")
        ]
    )
    def test_execute_with_exceptions(self, mocker, p_exception, p_result):
        module_arguments = {"test": "argument"}
        mocker.patch(f"{self.path}.parse_command", return_value=(Mock, Mock))
        process_mock = mocker.patch("subprocess.run")
        process_mock.side_effect = p_exception

        result = Module(module_arguments).execute()

        assert result == ModuleOutput(Result.FAIL, p_result, {})

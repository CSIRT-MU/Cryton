import json
import subprocess
from unittest.mock import Mock
import mod
import pytest


@pytest.mark.parametrize(
    "p_arguments, p_command",
    [
        ({"target": "http://address/index.php", "options": "--request-timeout 60"},
         ['wpscan', '--url', 'http://address/index.php', '-f', 'json', '--request-timeout', '60']),
        ({"custom_command": "test command"}, ["test", "command"]),
    ]
)
def test_parse_command(p_arguments, p_command):
    command = mod.parse_command(p_arguments)
    assert command == p_command


@pytest.mark.parametrize(
    "p_stdout, p_stderr, p_final_output",
    [
        ("test_output", "", "test_output"),
        ("test_output\n", "test_error", "test_output\ntest_error"),
    ]
)
def test_execute_with_standard_output(mocker, p_stdout, p_stderr, p_final_output):
    module_arguments = {"test": "argument"}
    validate_mock = mocker.patch("mod.validate")
    mocker.patch("mod.parse_command", return_value=["test", "command"])
    completed_process_mock = mocker.patch("subprocess.CompletedProcess")
    completed_process_mock.stdout.decode.return_value = p_stdout
    completed_process_mock.stderr.decode.return_value = p_stderr
    process_mock = mocker.patch("subprocess.run")
    process_mock.return_value = completed_process_mock

    result = mod.execute(module_arguments)

    validate_mock.assert_called_once_with(module_arguments)
    process_mock.assert_called_once_with(["test", "command"], capture_output=True)
    assert result == {
        mod.OUTPUT: p_final_output,
        mod.SERIALIZED_OUTPUT: {},
        mod.RETURN_CODE: 0
    }


def test_execute_with_json_output(mocker):
    module_arguments = {"test": "argument"}
    validate_mock = mocker.patch("mod.validate")
    mocker.patch("mod.parse_command", return_value=["test", "command"])
    completed_process_mock = mocker.patch("subprocess.CompletedProcess")
    completed_process_mock.stdout.decode.return_value = '{"test": "output"}'
    completed_process_mock.stderr.decode.return_value = "test_error"
    process_mock = mocker.patch("subprocess.run")
    process_mock.return_value = completed_process_mock

    result = mod.execute(module_arguments)

    validate_mock.assert_called_once_with(module_arguments)
    process_mock.assert_called_once_with(["test", "command"], capture_output=True)
    assert result == {
        mod.OUTPUT: "test_error",
        mod.SERIALIZED_OUTPUT: {"test": "output"},
        mod.RETURN_CODE: 0
    }


@pytest.mark.parametrize(
    "p_exception, p_result",
    [
        (OSError("test_error"), "Check if your command starts with 'wpscan'. Original error: test_error"),
        (subprocess.SubprocessError("test_error"), "WPScan couldn't start. Original error: test_error")
    ]
)
def test_execute_with_exceptions(mocker, p_exception, p_result):
    module_arguments = {"test": "argument"}
    mocker.patch("mod.validate")
    mocker.patch("mod.parse_command", return_value=(Mock, Mock))
    process_mock = mocker.patch("subprocess.run")
    process_mock.side_effect = p_exception

    result = mod.execute(module_arguments)

    assert result == {
        mod.OUTPUT: p_result,
        mod.SERIALIZED_OUTPUT: {},
        mod.RETURN_CODE: -1
    }

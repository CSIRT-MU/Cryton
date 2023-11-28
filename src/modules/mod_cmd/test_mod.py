import subprocess
from unittest.mock import patch
from pytest_mock import MockerFixture
import mod
import pytest


def test_execute_with_session_id(mocker: MockerFixture):
    args = {'cmd': "test", "session_id": 1}

    metasploit_mock = mocker.patch("mod.Metasploit")
    metasploit_mock.return_value.execute_in_session.return_value = "test_output"
    result = mod.execute(args)
    assert result == {
        "return_code": 0,
        "output": "test_output",
        "serialized_output": {},
    }


def test_execute_with_session_id_and_serialized_output(mocker: MockerFixture):
    args = {'cmd': "test", "session_id": 1, "serialized_output": True}

    metasploit_mock = mocker.patch("mod.Metasploit")
    metasploit_mock.return_value.execute_in_session.return_value = 'test "output"'
    result = mod.execute(args)
    assert result == {
        "return_code": 0,
        "output": 'test "output"',
        "serialized_output": {"auto_serialized": "output"},
    }


def test_execute_with_session_id_and_serialized_output_error(mocker: MockerFixture):
    args = {'cmd': "test", "session_id": 1, "serialized_output": True}

    metasploit_mock = mocker.patch("mod.Metasploit")
    metasploit_mock.return_value.execute_in_session.return_value = 'test output'
    result = mod.execute(args)
    assert result == {
        "return_code": -1,
        "output": 'test output\nserialized_output_error: Output of the script is not valid JSON.',
        "serialized_output": {},
    }


def test_execute_with_session_id_exception(mocker: MockerFixture):
    metasploit_mock = mocker.patch("mod.Metasploit")
    metasploit_mock.return_value.execute_in_session.side_effect = Exception("test_error")
    result = mod.execute({'cmd': "test", "session_id": 1})

    assert result == {
        "return_code": -1,
        "output": "test_error",
        "serialized_output": {},
    }


@pytest.mark.parametrize(
    "p_process_stdout, p_process_stderr, mod_output",
    [
        ("test_output", None, {'output': 'test_output\nNone', 'return_code': 0, 'serialized_output': {}}),
        (None, "test_error", {'output': 'None\ntest_error', 'return_code': -1, 'serialized_output': {}})
    ]
)
def test_execute_without_session_id(mocker: MockerFixture, p_process_stdout, p_process_stderr, mod_output):
    process_mock = mocker.patch("subprocess.CompletedProcess")
    process_mock.stdout.decode.return_value = p_process_stdout
    process_mock.stderr.decode.return_value = p_process_stderr

    mocker.patch("subprocess.run", return_value=process_mock)
    args = {"cmd": "test"}
    result = mod.execute(args)

    process_mock.check_returncode.assert_called_once()
    assert result == mod_output


def test_execute_without_session_id_and_serialized_output(mocker: MockerFixture):
    process_mock = mocker.patch("subprocess.CompletedProcess")
    process_mock.stdout.decode.return_value = '"output"'
    process_mock.stderr.decode.return_value = ''

    mocker.patch("subprocess.run", return_value=process_mock)
    args = {"cmd": "test", "serialized_output": True}
    result = mod.execute(args)

    process_mock.check_returncode.assert_called_once()
    assert result == {
        "return_code": 0,
        "output": '"output"\n',
        "serialized_output": {"auto_serialized": "output"},
    }


def test_execute_without_session_id_exceptions(mocker: MockerFixture):
    args = {"cmd": "test"}
    encoded_error = "test_error".encode("utf-8")

    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("test", 10)):
        result = mod.execute(args)
        assert result == {
            "output": "Command execution timed out",
            "serialized_output": {},
            "return_code": -1
        }

    with patch("subprocess.CompletedProcess.check_returncode",
               side_effect=subprocess.CalledProcessError(-1, "test", stderr=encoded_error)):
        result = mod.execute(args)
        assert result == {
            "output": "test_error",
            "serialized_output": {},
            "return_code": -1
        }

    with patch("subprocess.run", side_effect=Exception("test_exception")):
        mocker.patch("traceback.format_exc", return_value="test_traceback")
        result = mod.execute(args)
        assert result == {
            "output": "test_exception\ntest_traceback",
            "serialized_output": {},
            "return_code": -1
        }

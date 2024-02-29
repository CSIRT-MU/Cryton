import subprocess
from unittest.mock import Mock, patch
import pytest
from pytest_mock import MockerFixture

from cryton.modules.ffuf import mod


@pytest.fixture
def ffuf_arguments():
    return {
        "target": "address", "serialized_output": True, "wordlist": "/path/to/wordlist", "options": "-X POST"
    }


@pytest.fixture
def mock_subprocess_run(mocker):
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.stdout.decode.return_value = "/'___\ /'___\ /'___\ /\ \__/ /\ \__/ __ __ /\ \__/ \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\ \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/ \ \_\ \ \_\ \ \____/ \ \_\ \/_/ \/_/ \/___/ \/_/ v2.0.0-dev ________________________________________________ :: Method : POST :: URL : http://172.16.169.128/FUZZ :: Wordlist : FUZZ: /usr/share/wordlists/dirb/small.txt :: Follow redirects : false :: Calibration : false :: Timeout : 10 :: Threads : 40 :: Matcher : Response status: 200,204,301,302,307,401,403,405,500 ________________________________________________ [2K:: Progress: [4/959] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 :: [2K:: Progress: [489/959] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 :: [2K:: Progress: [958/959] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 :: [2K:: Progress: [959/959] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 :: [2K:: Progress: [959/959] :: Job [1/1] :: 197 req/sec :: Duration: [0:00:01] :: Errors: 0 :: "
    mock_run.return_value.stderr.decode.return_value = "test_error"
    return mock_run


@pytest.mark.parametrize(
    "p_arguments, p_command",
    [
        ({ "target": "http://127.0.0.1/FUZZ", "wordlist": "/usr/share/wordlists/dirb/small.txt", "options": "-X POST", "serialized_output": False}, ["ffuf", "-w", "/usr/share/wordlists/dirb/small.txt", "-u", "http://127.0.0.1/FUZZ", "-X", "POST" ]),
        ({ "target": "http://127.0.0.1/FUZZ", "wordlist": "/usr/share/wordlists/dirb/small.txt", "options": "", "serialized_output": False}, ["ffuf", "-w", "/usr/share/wordlists/dirb/small.txt", "-u", "http://127.0.0.1/FUZZ", "" ]),
        ({ "target": "http://198.51.100.1/FUZZ", "wordlist": "/usr/share/wordlists/dirb/small.txt", "options": None, "serialized_output": False}, ["ffuf", "-w", "/usr/share/wordlists/dirb/small.txt", "-u", "http://198.51.100.1/FUZZ"]),
    ]
)

def test_parse_command(p_arguments, p_command):
    command = mod.parse_command(p_arguments)
    assert command == p_command


def test_execute_with_arguments(mocker, mock_subprocess_run, ffuf_arguments):
    validate_mock = mocker.patch("mod.validate")
    parse_command_mock = mocker.patch("mod.parse_command", return_value=["test_subprocess_result"])

    result = mod.execute(ffuf_arguments)
    validate_mock.assert_called_once_with(ffuf_arguments)
    parse_command_mock.assert_called_once_with(ffuf_arguments)
    mock_subprocess_run.assert_called_once_with(["test_subprocess_result"], capture_output=True)


def test_execute_exeptions(mocker, ffuf_arguments):
    mocker.patch("mod.validate")
    with patch("mod.subprocess.run", side_effect=subprocess.SubprocessError("test_error")):
        result = mod.execute(ffuf_arguments)
        assert result == {
            "return_code": -1,
            "output": "ffuf couldn't start. Original Error: test_error",
            "serialized_output": {}
        }
 

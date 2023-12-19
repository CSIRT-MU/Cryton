import socket

import mod
import pytest
from pytest_mock import MockerFixture


@pytest.fixture()
def module_arguments():
    return {
        'module_type': 'exploit',
        'module': 'test/module',
        'module_options': {"RHOSTS": "address"},
        'payload': 'test/payload',
        'payload_options': {"LHOST": "address"},
        'module_timeout': 5
    }


@pytest.fixture
def f_get_host_by_name(mocker: MockerFixture):
    return mocker.patch("socket.gethostbyname")


@pytest.fixture
def f_inet_aton(mocker: MockerFixture):
    return mocker.patch("socket.inet_aton")


@pytest.mark.parametrize(
    "p_sessions_after, p_result",
    [
        (["1", "2"], "2"),
        (["1"], None)
    ]
)
def test_get_created_session(mocker, p_sessions_after, p_result):
    msf_mock = mocker.patch("mod.Metasploit")
    mocker.patch("mod.Metasploit.get_sessions", return_value=p_sessions_after)
    result = mod.get_created_session(msf_mock, "test_target", "test_exploit", "test_payload", ["1"])

    assert result == p_result


def test_create_msf_command(mocker, module_arguments):
    mocker.patch("mod.isinstance")
    exploit_mock = mocker.patch("pymetasploit3.msfrpc.ExploitModule")
    payload_mock = mocker.patch("mod.PayloadModule")

    exploit_mock.modulename = (module_arguments["module"])
    exploit_mock.runoptions = (module_arguments["module_options"])
    exploit_mock.moduletype = (module_arguments["module_type"])
    exploit_mock.payloads = (module_arguments["payload"])
    exploit_mock.target = "test_mod_target"
    payload_mock.modulename = (module_arguments["payload"])
    payload_mock.runoptions = (module_arguments["payload_options"])
    result = mod.create_msf_command(exploit_mock, payload_mock, False)
    expected_command = f"use exploit/{exploit_mock.modulename}\nset payload {payload_mock.modulename}\n" \
                       f"set LHOST address\nset RHOSTS address\nset TARGET {exploit_mock.target}\nrun -z"
    assert result == expected_command


def test_run_module_with_output(mocker):
    msf_console_mock = mocker.patch("mod.MsfConsole")
    mocker.patch("time.sleep")
    mock_time = mocker.patch("time.time")
    mock_time.side_effect = [0, 1]

    msf_console_mock.read.return_value = {"data": "data"}
    msf_console_mock.is_busy.return_value = False
    result = mod.run_module_with_output(msf_console_mock, "use payload\nset key value\nrun -z", 1)
    msf_console_mock.write.assert_called_with("use payload\nset key value\nrun -z")
    assert result == "data"


def test_get_session_target_ip(f_get_host_by_name, f_inet_aton):
    module_options = {"rhosts": "address address"}

    result = mod.get_session_target(module_options)

    assert result == "address"


def test_get_session_target_domain(f_get_host_by_name, f_inet_aton):
    module_options = {"rhosts": "address address"}

    f_inet_aton.side_effect = OSError
    f_get_host_by_name.return_value = "address"

    result = mod.get_session_target(module_options)

    assert result == "address"


@pytest.mark.parametrize(
    "module_options",
    [
        ({"rhosts": "address address"}),
        ({"rhostss": "address"}),
    ]
)
def test_get_session_target_error(module_options, f_get_host_by_name, f_inet_aton):
    f_get_host_by_name.side_effect = socket.gaierror
    f_inet_aton.side_effect = OSError

    result = mod.get_session_target(module_options)

    assert result is None


@pytest.mark.parametrize(
    "p_exploit_result, p_created_session, p_module_result",
    [
        ("[+] Success test data", "1",
         {"return_code": 0, "serialized_output": {"session_id": "1"}, "output": "[+] Success test data\n"}),

        ("[-] Exploit failed", None,
         {"return_code": -1, "serialized_output": {}, "output": "[-] Exploit failed\n"}),

        ("Test output", None,
         {"return_code": -1, "serialized_output": {}, "output": "Test output\n"})
    ]
)
def test_execute(p_exploit_result, p_module_result, p_created_session, module_arguments, mocker):
    mocker.patch("mod.get_created_session", return_value=p_created_session)
    mocker.patch("mod.get_session_target", return_value="test")
    metasploit_mock = mocker.patch("mod.Metasploit")
    mocker.patch("mod.create_msf_command")
    mocker.patch("mod.run_module_with_output", return_value=p_exploit_result)

    result = mod.execute(module_arguments)

    assert result == p_module_result
    metasploit_mock.return_value.is_connected.assert_called_once()

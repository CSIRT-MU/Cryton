import socket
from pytest_mock import MockerFixture
import pytest
from dataclasses import asdict

from cryton.modules.metasploit.module import (
    Module, get_session_target, get_created_session, run_module_with_output, create_msf_command
)


class TestModuleMetasploit:
    path = "cryton.modules.metasploit.module"
    @pytest.fixture()
    def module_arguments(self):
        return {
            'module_type': 'exploit',
            'module': 'test/module',
            'module_options': {"RHOSTS": "address"},
            'payload': 'test/payload',
            'payload_options': {"LHOST": "address"},
            'module_timeout': 5
        }

    @pytest.fixture
    def f_get_host_by_name(self, mocker: MockerFixture):
        return mocker.patch("socket.gethostbyname")

    @pytest.fixture
    def f_inet_aton(self, mocker: MockerFixture):
        return mocker.patch("socket.inet_aton")

    @pytest.mark.parametrize(
        "p_arguments",
        [
            {
                "session_filter": {
                    "type": "a",
                    "tunnel_local": "a",
                    "tunnel_peer": "a",
                    "via_exploit": "a",
                    "via_payload": "a",
                    "desc": "a",
                    "info": "a",
                    "workspace": "a",
                    "session_host": "a",
                    "session_port": 1,
                    "target_host": "a",
                    "username": "a",
                    "uuid": "a",
                    "exploit_uuid": "a",
                    "routes": "a",
                    "arch": "a",
                    "platform": "a"
                },
                "ignore_old_sessions": True,
                "module_type": "exploit",
                "module": "placeholder",
                "wait_for_result": True,
                "module_retries": 1,
                "module_timeout": 1,
                "module_options": {"example": "example"},
                "payload": "placeholder",
                "payload_options": {"example": "example"},
            },
            {
                "session_filter": {},
                "module_type": "exploit",
                "module": "placeholder",
                "module_options": {},
                "payload": "placeholder",
                "payload_options": {},
            },
            {
                "module_type": "exploit",
                "module": "placeholder",
                "payload": "placeholder",
            },
            {
                "module_type": "exploit",
                "module": "placeholder",
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
            {
                "session_filter": {
                    "non_existent": "a",
                },
                "module_type": "exploit",
                "module": "placeholder",
            },
            # {  # TODO: this case is uncaught because of an incorrect schema
            #     "module_type": "post",
            #     "module": "placeholder",
            #     "payload": "placeholder"
            # },
            {
                "module_type": "post",
            },
            {
                "module": "placeholder",
            },
        ]
    )
    def test_schema_error(self, p_arguments: dict):
        with pytest.raises(Exception):
            Module.validate_arguments(p_arguments)

    def test_check_requirements_command(self):
        module = Module({})

        assert module.check_requirements() is None

    @pytest.mark.parametrize(
        "p_sessions_after, p_result",
        [
            ([1, 2], 2),
            ([1], None)
        ]
    )
    def test_get_created_session(self, mocker, p_sessions_after, p_result):
        msf_mock = mocker.patch(f"{self.path}.Metasploit")
        mocker.patch(f"{self.path}.Metasploit.get_sessions", return_value=p_sessions_after)
        result = get_created_session(msf_mock, [1])

        assert result == p_result

    def test_create_msf_command(self, mocker, module_arguments):
        mocker.patch(f"{self.path}.isinstance")
        exploit_mock = mocker.patch("pymetasploit3.msfrpc.ExploitModule")
        payload_mock = mocker.patch(f"{self.path}.PayloadModule")

        exploit_mock.modulename = (module_arguments["module"])
        exploit_mock.runoptions = (module_arguments["module_options"])
        exploit_mock.moduletype = (module_arguments["module_type"])
        exploit_mock.payloads = (module_arguments["payload"])
        exploit_mock.target = "test_mod_target"
        payload_mock.modulename = (module_arguments["payload"])
        payload_mock.runoptions = (module_arguments["payload_options"])
        result = create_msf_command(exploit_mock, payload_mock, False)
        expected_command = f"use exploit/{exploit_mock.modulename}\nset payload {payload_mock.modulename}\n" \
                           f"set LHOST address\nset RHOSTS address\nset TARGET {exploit_mock.target}\nrun -z"
        assert result == expected_command

    def test_run_module_with_output(self, mocker):
        msf_console_mock = mocker.patch(f"{self.path}.MsfConsole")
        mocker.patch("time.sleep")
        mock_time = mocker.patch("time.time")
        mock_time.side_effect = [0, 1]

        msf_console_mock.read.return_value = {"data": "data"}
        msf_console_mock.is_busy.return_value = False
        result = run_module_with_output(msf_console_mock, "use payload\nset key value\nrun -z", 1)
        msf_console_mock.write.assert_called_with("use payload\nset key value\nrun -z")
        assert result == "data"

    def test_get_session_target_ip(self, f_get_host_by_name, f_inet_aton):
        module_options = {"rhosts": "address address"}

        result = get_session_target(module_options)

        assert result == "address"

    def test_get_session_target_domain(self, f_get_host_by_name, f_inet_aton):
        module_options = {"rhosts": "address address"}

        f_inet_aton.side_effect = OSError
        f_get_host_by_name.return_value = "address"

        result = get_session_target(module_options)

        assert result == "address"

    @pytest.mark.parametrize(
        "p_module_options",
        [
            ({"rhosts": "address address"}),
            ({"rhostss": "address"}),
        ]
    )
    def test_get_session_target_error(self, p_module_options, f_get_host_by_name, f_inet_aton):
        f_get_host_by_name.side_effect = socket.gaierror
        f_inet_aton.side_effect = OSError

        result = get_session_target(p_module_options)

        assert result is None

    @pytest.mark.parametrize(
        "p_exploit_result, p_created_session, p_module_result",
        [
            ("[+] Success test data", "1",
             {"result": "ok", "serialized_output": {"session_id": "1"}, "output": "[+] Success test data\n"}),

            ("[-] Exploit failed", None,
             {"result": "fail", "serialized_output": {}, "output": "[-] Exploit failed\n"}),

            ("Test output", None,
             {"result": "fail", "serialized_output": {}, "output": "Test output\n"})
        ]
    )
    def test_execute(self, p_exploit_result, p_module_result, p_created_session, module_arguments, mocker):
        mocker.patch(f"{self.path}.get_created_session", return_value=p_created_session)
        mocker.patch(f"{self.path}.get_session_target", return_value="test")
        metasploit_mock = mocker.patch(f"{self.path}.Metasploit")
        mocker.patch(f"{self.path}.create_msf_command")
        mocker.patch(f"{self.path}.run_module_with_output", return_value=p_exploit_result)

        result = Module(module_arguments).execute()

        assert asdict(result) == p_module_result
        metasploit_mock.return_value.is_connected.assert_called_once()

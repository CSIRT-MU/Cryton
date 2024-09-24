from unittest.mock import Mock
from pytest_mock import MockerFixture
import pytest
from dataclasses import asdict

from cryton.modules.nmap.module import (
    Module,
    execute_scan,
    filter_nmap_output_ports,
    match_cpe_in_port_parameters,
    compare_found_ports_with_port_parameters,
    parse_custom_command,
    Result,
)


class TestModuleNmap:
    path = "cryton.modules.nmap.module"

    @pytest.mark.parametrize(
        "p_arguments",
        [
            {
                "target": "example",
                "ports": [1],
                "options": "a b",
                "timeout": 1,
                "port_parameters": [
                    {
                        "portid": "a",
                        "host": "a",
                        "protocol": "a",
                        "state": "a",
                        "reason": "a",
                        "cpe": ["a"],
                        "scripts": ["a"],
                        "service": {
                            "name": "a",
                            "product": "a",
                            "version": "a",
                            "extrainfo": "a",
                            "ostype": "a",
                            "method": "a",
                            "conf": "a",
                        },
                    }
                ],
            },
            {
                "target": "example",
                "port_parameters": [
                    {
                        "portid": "a",
                        "host": "a",
                        "protocol": "a",
                        "state": "a",
                        "reason": "a",
                        "cpe": ["a"],
                        "scripts": ["a"],
                        "service": {},
                    }
                ],
            },
            {"target": "example", "port_parameters": []},
            {
                "target": "example",
            },
        ],
    )
    def test_schema(self, p_arguments: dict):
        Module.validate_arguments(p_arguments)

    @pytest.mark.parametrize(
        "p_arguments",
        [
            {"command": "placeholder"},
            {"command": "placeholder", "serialize_output": True, "timeout": 1, "port_parameters": [{"portid": "a"}]},
        ],
    )
    def test_schema_custom(self, p_arguments: dict):
        Module.validate_arguments(p_arguments)

    @pytest.mark.parametrize(
        "p_arguments",
        [
            {},
            {"non_existent": "placeholder"},
            {"target": "placeholder", "command": "placeholder"},
        ],
    )
    def test_schema_error(self, p_arguments: dict):
        with pytest.raises(Exception):
            Module.validate_arguments(p_arguments)

    def test_check_requirements_command(self):
        module = Module({})

        assert module.check_requirements() is None

    @pytest.fixture
    def f_re_match(self, mocker: MockerFixture):
        mock_match = mocker.patch("re.match")
        mock_match.return_value = True

    @pytest.mark.parametrize(
        "p_ports, p_scan_arg, p_options, p_arguments",
        [(None, "--top-ports 100", None, ""), ([1, 2], "", "test_option", "test_option -p1,2")],
    )
    def test_execute_scan(self, mocker, p_ports, p_scan_arg, p_arguments, p_options):
        nmap_client_mock = mocker.patch(f"{self.path}.nmap3.Nmap")
        nmap_client_mock.scan_command.return_value = "test_scan_result"

        result = execute_scan("test_target", p_options, p_ports, nmap_client_mock, 60)
        assert result == "test_scan_result"
        nmap_client_mock.scan_command.assert_called_once_with(
            target="test_target", arg=p_scan_arg, args=p_arguments, timeout=60
        )

    @pytest.mark.parametrize(
        "p_serialized_output, p_module_failed",
        [({"address": {"ports": [{"state": "closed"}]}}, True), ({"address": {"ports": [{"state": "open"}]}}, False)],
    )
    def test_filter_nmap_output_ports(self, mocker, f_re_match, p_serialized_output, p_module_failed):
        mocker.patch(f"{self.path}.compare_found_ports_with_port_parameters", return_value=True)

        result = filter_nmap_output_ports(p_serialized_output, [])
        assert result == p_module_failed

    @pytest.mark.parametrize(
        "p_found_cpes, p_desired_cpes, p_result",
        [
            ([{"cpe": "test_cpe"}, {"cpe": "Desired_Test_cpe"}], ["desired_test"], True),
            ([{"cpe": "test_cpe"}, {"cpe": "test_cpe2"}], ["desired_test"], False),
        ],
    )
    def test_match_cpe_in_port_parameters(self, p_found_cpes, p_desired_cpes, p_result):
        result = match_cpe_in_port_parameters(p_found_cpes, p_desired_cpes)
        assert result == p_result

    @pytest.mark.parametrize(
        "p_desired_port, p_port_result, p_result",
        [
            (
                {"service": {"test_service_key": "test_service_value"}, "desired_parameter": "desired_key"},
                {"service": {"test_service_key": "test_service_value"}, "desired_parameter": "desired_key"},
                True,
            ),
            (
                {"service": {"test_service_key": "test_service_value"}},
                {"service": {"test_service_key": "not_desired_service_value"}},
                False,
            ),
            ({"desired_parameter": "desired_key"}, {"desired_parameter": "different_key"}, False),
            ({"cpe": "test_cpe"}, {"cpe": "test_cpe"}, False),
        ],
    )
    def test_compare_found_ports_with_port_parameters(self, mocker, p_desired_port, p_port_result, p_result):
        mocker.patch(f"{self.path}.match_cpe_in_port_parameters", return_value=False)
        assert compare_found_ports_with_port_parameters(p_desired_port, p_port_result) == p_result

    def test_parse_custom_command(self):
        assert parse_custom_command(["test_parameter"]) == ["test_parameter", "-oX", "-"]

    def test_execute_custom_command(self, mocker):
        # declarations and mocks
        run_command_output_mock = "a"
        xml_root_mock = Mock()
        nmap_client_mock = mocker.patch(f"{self.path}.nmap3.Nmap")
        nmap_client_mock.return_value.run_command.return_value = run_command_output_mock
        nmap_client_mock.return_value.get_xml_et.return_value = xml_root_mock
        nmap_client_mock.return_value.parser.filter_top_ports.return_value = {"runtime": {"summary": ""}}
        mocker.patch(f"{self.path}.filter_nmap_output_ports", return_value=True)
        parse_custom_command_mock = mocker.patch(f"{self.path}.parse_custom_command")
        parse_custom_command_mock.return_value = ["test_parameter1", "test_parameter2"]

        # execution and asserts
        result = Module({"command": "test_command"}).execute()
        parse_custom_command_mock.assert_called_once_with(["test_command"])
        nmap_client_mock.return_value.run_command.assert_called_once_with(
            cmd=["test_parameter1", "test_parameter2"], timeout=60
        )
        nmap_client_mock.return_value.get_xml_et.assert_called_once_with(run_command_output_mock)
        nmap_client_mock.return_value.parser.filter_top_ports.assert_called_once_with(xml_root_mock)

        assert asdict(result) == {
            "output": run_command_output_mock,
            "result": Result.OK,
            "serialized_output": {"runtime": {"summary": ""}},
        }

    @pytest.mark.parametrize(
        "p_filter_nmap_output_ports_output, p_return_code, p_output",
        [
            (True, "fail", "test_output"),
            (False, "ok", "test_output"),
        ],
    )
    def test_execute_with_arguments(self, mocker, p_filter_nmap_output_ports_output, p_return_code, p_output):
        # declarations and mocks
        nmap_arguments = {
            "target": "test_target",
            "ports": [1 - 30, 80],
            "options": "-T4 -sV",
            "raw_output": True,
            "port_parameters": [{"portid": "80", "state": "open"}],
        }
        xml_root_mock = Mock()
        nmap_client_mock = mocker.patch(f"{self.path}.nmap3.Nmap")
        execute_scan_mock = mocker.patch(f"{self.path}.execute_scan")
        execute_scan_mock.return_value = xml_root_mock
        nmap_client_mock.return_value.parser.filter_top_ports.return_value = {"runtime": {"summary": ""}}
        filter_nmap_output_ports_mock = mocker.patch(
            f"{self.path}.filter_nmap_output_ports", return_value=p_filter_nmap_output_ports_output
        )
        mocker.patch(f"{self.path}.ElementTree.tostring", return_value="test_output")

        # execution and asserts
        result = Module(nmap_arguments).execute()
        execute_scan_mock.assert_called_once_with(
            nmap_arguments["target"],
            nmap_arguments["options"],
            nmap_arguments["ports"],
            nmap_client_mock.return_value,
            60,
        )
        filter_nmap_output_ports_mock.assert_called_once_with(
            {"runtime": {"summary": ""}}, nmap_arguments["port_parameters"]
        )
        nmap_client_mock.return_value.parser.filter_top_ports.assert_called_once_with(xml_root_mock)

        assert asdict(result) == {
            "output": p_output,
            "result": p_return_code,
            "serialized_output": {"runtime": {"summary": ""}},
        }

    def test_execute_with_unreachable_target(self, mocker):
        nmap_arguments = {"target": "test_target"}
        mocker.patch(f"{self.path}.execute_scan")
        mocker.patch(f"{self.path}.ElementTree.tostring")
        nmap_client_mock = mocker.patch(f"{self.path}.nmap3.Nmap")
        nmap_client_mock.return_value.parser.filter_top_ports.return_value = {"runtime": {"summary": "0 hosts up"}}

        result = Module(nmap_arguments).execute()

        assert asdict(result) == {
            "output": "Provided target is not up or not reachable",
            "result": "fail",
            "serialized_output": {"runtime": {"summary": "0 hosts up"}},
        }

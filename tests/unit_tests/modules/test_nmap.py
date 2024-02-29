from unittest.mock import Mock
import pytest
from pytest_mock import MockerFixture

from cryton.modules.nmap import mod

@pytest.fixture
def f_re_match(mocker: MockerFixture):
    mock_match = mocker.patch("re.match")
    mock_match.return_value = True


@pytest.mark.parametrize(
    "p_ports, p_scan_arg, p_options, p_arguments",
    [
        (None, "--top-ports 100", None, ""),
        ([1, 2], "", "test_option", "test_option -p1,2")
    ]
)
def test_execute_scan(mocker, p_ports, p_scan_arg, p_arguments, p_options):
    nmap_client_mock = mocker.patch("mod.nmap3.Nmap")
    nmap_client_mock.scan_command.return_value = "test_scan_result"

    result = mod.execute_scan("test_target", p_options, p_ports, nmap_client_mock, 60)
    assert result == "test_scan_result"
    nmap_client_mock.scan_command.assert_called_once_with(target="test_target", arg=p_scan_arg, args=p_arguments,
                                                          timeout=60)


@pytest.mark.parametrize(
    "p_serialized_output, p_module_failed",
    [
        ({"address": {"ports": [{"state": "closed"}]}}, True),
        ({"address": {"ports": [{"state": "open"}]}}, False)
    ]
)
def test_filter_nmap_output_ports(mocker, f_re_match, p_serialized_output, p_module_failed):
    mocker.patch("mod.compare_found_ports_with_port_parameters", return_value=True)

    result = mod.filter_nmap_output_ports(p_serialized_output, [])
    assert result == p_module_failed


@pytest.mark.parametrize(
    "p_found_cpes, p_desired_cpes, p_result",
    [
        ([{"cpe": "test_cpe"}, {"cpe": "Desired_Test_cpe"}], ["desired_test"], True),
        ([{"cpe": "test_cpe"}, {"cpe": "test_cpe2"}], ["desired_test"], False)
    ]
)
def test_match_cpe_in_port_parameters(p_found_cpes, p_desired_cpes, p_result):
    result = mod.match_cpe_in_port_parameters(p_found_cpes, p_desired_cpes)
    assert result == p_result


@pytest.mark.parametrize(
    "p_desired_port, p_port_result, p_result",
    [
        ({"service": {"test_service_key": "test_service_value"}, "desired_parameter": "desired_key"},
         {"service": {"test_service_key": "test_service_value"}, "desired_parameter": "desired_key"},
         True),
        ({"service": {"test_service_key": "test_service_value"}},
         {"service": {"test_service_key": "not_desired_service_value"}},
         False),
        ({"desired_parameter": "desired_key"},
         {"desired_parameter": "different_key"},
         False),
        ({"cpe": "test_cpe"},
         {"cpe": "test_cpe"},
         False),
    ]
)
def test_compare_found_ports_with_port_parameters(mocker, p_desired_port, p_port_result, p_result):
    mocker.patch("mod.match_cpe_in_port_parameters", return_value=False)
    assert mod.compare_found_ports_with_port_parameters(p_desired_port, p_port_result) == p_result


def test_parse_custom_command():
    assert mod.parse_custom_command(["test_parameter"]) == ["test_parameter", "-oX", "-"]


def test_execute_custom_command(mocker):
    # declarations and mocks
    run_command_output_mock = Mock()
    xml_root_mock = Mock()
    nmap_client_mock = mocker.patch("mod.nmap3.Nmap")
    nmap_client_mock.return_value.run_command.return_value = run_command_output_mock
    nmap_client_mock.return_value.get_xml_et.return_value = xml_root_mock
    nmap_client_mock.return_value.parser.filter_top_ports.return_value = {"runtime": {"summary": ""}}
    mocker.patch("mod.validate")
    mocker.patch("mod.filter_nmap_output_ports", return_value=True)
    parse_custom_command_mock = mocker.patch("mod.parse_custom_command")
    parse_custom_command_mock.return_value = ["test_parameter1", "test_parameter2"]

    # execution and asserts
    result = mod.execute({"command": "test_command"})
    parse_custom_command_mock.assert_called_once_with(["test_command"])
    nmap_client_mock.return_value.run_command.assert_called_once_with(cmd=["test_parameter1", "test_parameter2"],
                                                                      timeout=60)
    nmap_client_mock.return_value.get_xml_et.assert_called_once_with(run_command_output_mock)
    nmap_client_mock.return_value.parser.filter_top_ports.assert_called_once_with(xml_root_mock)

    assert result == {
        "output": run_command_output_mock,
        "return_code": 0,
        "serialized_output": {"runtime": {"summary": ""}}
    }


@pytest.mark.parametrize(
    "p_filter_nmap_output_ports_output, p_return_code, p_output",
    [
        (True, -1, "test_output"),
        (False, 0, "test_output"),
    ]
)
def test_execute_with_arguments(mocker, p_filter_nmap_output_ports_output, p_return_code, p_output):
    # declarations and mocks
    nmap_arguments = {
        "target": "test_target",
        "ports": [1-30, 80],
        "options": "-T4 -sV",
        "raw_output": True,
        "port_parameters": [
            {"portid": "80", "state": "open"}
        ]
    }
    xml_root_mock = Mock()
    nmap_client_mock = mocker.patch("mod.nmap3.Nmap")
    execute_scan_mock = mocker.patch("mod.execute_scan")
    execute_scan_mock.return_value = xml_root_mock
    nmap_client_mock.return_value.parser.filter_top_ports.return_value = {"runtime": {"summary": ""}}
    mocker.patch("mod.validate")
    filter_nmap_output_ports_mock = mocker.patch("mod.filter_nmap_output_ports",
                                                 return_value=p_filter_nmap_output_ports_output)
    mocker.patch("mod.ElementTree.tostring", return_value="test_output")

    # execution and asserts
    result = mod.execute(nmap_arguments)
    execute_scan_mock.assert_called_once_with(nmap_arguments["target"], nmap_arguments["options"],
                                              nmap_arguments["ports"], nmap_client_mock.return_value, 60)
    filter_nmap_output_ports_mock.assert_called_once_with({"runtime": {"summary": ""}},
                                                          nmap_arguments["port_parameters"])
    nmap_client_mock.return_value.parser.filter_top_ports.assert_called_once_with(xml_root_mock)

    assert result == {
        "output": p_output,
        "return_code": p_return_code,
        "serialized_output": {"runtime": {"summary": ""}}
    }


def test_execute_with_unreachable_target(mocker):
    nmap_arguments = {"target": "test_target"}
    mocker.patch("mod.validate")
    mocker.patch("mod.execute_scan")
    mocker.patch("mod.ElementTree.tostring")
    nmap_client_mock = mocker.patch("mod.nmap3.Nmap")
    nmap_client_mock.return_value.parser.filter_top_ports.return_value = {"runtime": {"summary": "0 hosts up"}}

    result = mod.execute(nmap_arguments)

    assert result == {
        "output": "Provided target is not up or not reachable",
        "return_code": -1,
        "serialized_output": {"runtime": {"summary": "0 hosts up"}}
    }

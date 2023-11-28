from typing import Optional as OptionalType
import re
from xml.etree import ElementTree
import nmap3
from schema import Schema, Optional, Use, SchemaError
from copy import deepcopy

from cryton_worker.lib.util.module_util import OUTPUT, SERIALIZED_OUTPUT, RETURN_CODE


def validate(arguments: dict) -> int:
    """
    Validate input values for the execute function.

    :param arguments: Arguments for module execution
    :return: 0 If arguments are valid
    :raises: Schema Exception
    """

    port_parameters_validation = [
            {
                Optional("portid"): Use(str),
                Optional("host"): str,
                Optional("protocol"): str,
                Optional("state"): str,
                Optional("reason"): str,
                Optional("cpe"): list,
                Optional("service"):
                    {
                        Optional("name"): Use(str),
                        Optional("product"): Use(str),
                        Optional("version"): Use(str),
                        Optional("extrainfo"): Use(str),
                        Optional("ostype"): Use(str),
                        Optional("method"): Use(str),
                        Optional("conf"): Use(str),
                    }
            }
        ]

    default_schema = Schema({
        "target": str,
        Optional("ports"): [Use(int)],
        Optional("port_parameters"): port_parameters_validation,
        Optional("options"): str,
        Optional("raw_output"): bool,
        Optional("timeout"): int,
    })

    custom_command_validation = {
        "command": str,
        Optional("timeout"): int,
        Optional("serialized_output"): bool,
        Optional("raw_output"): bool,
    }

    if "command" in arguments.keys():
        if "format_output" not in arguments.keys() or arguments.get("format_output") is True:
            custom_command_validation[Optional("port_parameters")] = port_parameters_validation
        Schema(custom_command_validation).validate(arguments)
    else:
        default_schema.validate(arguments)

    return 0


def execute_scan(target: str, options: OptionalType[str], ports: OptionalType[list], nmap_client: nmap3.Nmap,
                 timeout: int) -> ElementTree.Element:
    """
    Executes Nmap scan from predefined parameters.
    :param target: Target of nmap scan
    :param options: Additional Nmap parameters
    :param ports: Specific ports for scan
    :param nmap_client: Nmap class from nmap3 library
    :param timeout: Timeout for nmap scan
    :return: Parsed Nmap scan result
    """
    arguments = ""
    if options is not None:
        arguments = options
    if ports is not None:
        ports_string = " -p" + ",".join(list(map(str, ports)))
        arguments += ports_string
        return nmap_client.scan_command(target=target, arg="", args=arguments, timeout=timeout)
    return nmap_client.scan_command(target=target, arg="--top-ports 100", args=arguments, timeout=timeout)


def filter_nmap_output_ports(serialized_output: dict, desired_port_parameters: list) -> [bool]:
    """
    Filter ports that are open and meets desired_port_parameters if specified.
    Decide if module execution failed based on desired_port_parameters.

    :param serialized_output: Output of scan_from_parameters function
    :param desired_port_parameters: Ports with a specific parameters that you want to return
    :return: [Open ports that meets desired_port_parameters if not None,
    Bool value representing if the module failed or not]
    """
    module_failed = True
    for key in serialized_output.keys():
        if re.match("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", key):
            ports_result = deepcopy(serialized_output[key]["ports"])
            for port in serialized_output[key]["ports"]:
                if port["state"] != "open":
                    serialized_output[key]["ports"].remove(port)
                    ports_result.remove(port)
                    continue
                for each_port in desired_port_parameters:
                    # check if host in port_parameters is in scan result if target is subnet
                    if compare_found_ports_with_port_parameters(each_port, port) is False:
                        ports_result.remove(port)
            if ports_result:
                module_failed = False

    return module_failed


def match_cpe_in_port_parameters(found_cpes: list, desired_cpes: list):
    list_of_cpe_values = []

    for cpe_dict in found_cpes:
        list_of_cpe_values.append(cpe_dict.values())
        for found_cpe in cpe_dict.values():
            for desired_cpe in desired_cpes:
                if desired_cpe.lower() in found_cpe.lower():
                    return True
    return False


def compare_found_ports_with_port_parameters(desired_port: dict, port_results: dict) -> bool:
    """
    Check if port meets given desired port parameters and if yes return True, else return False.

    :param desired_port: Desired parameters that port should meet
    :param port_results: Parameters of specific port found by scan
    :return: Bool value representing whether desired port parameters match any found port in scan result
    """
    for key, value in desired_port.items():
        if key in port_results.keys():
            if key == "service":
                for service_key, service_value in desired_port[key].items():
                    if service_key in port_results[key].keys():
                        if service_value.lower() not in port_results[key][service_key].lower():
                            return False
            else:
                if key == "cpe":
                    if not match_cpe_in_port_parameters(port_results[key], desired_port[key]):
                        return False
                else:
                    if value.lower() not in port_results[key].lower():
                        return False
    return True


def parse_custom_command(list_of_command_parameters: list):
    if "-oX" in list_of_command_parameters:
        return list_of_command_parameters
    else:
        list_of_command_parameters.insert(1, "-oX")
        list_of_command_parameters.insert(2, "-")
        return list_of_command_parameters


def execute(arguments: dict) -> dict:
    """
    Takes arguments in form of dictionary and runs Nmap based on them.

    :param arguments: Arguments from which is compiled and ran nmap command and parsed wanted output
    :return: Module output containing:
                return_code (0-success, 1-fail, 2-err),
                output (raw output),
                serialized_output (parsed output that can be used in other modules),
    """
    ret_vals = {
        RETURN_CODE: -1,
        OUTPUT: "",
        SERIALIZED_OUTPUT: {}
    }

    try:
        validate(arguments)
    except SchemaError as err:
        ret_vals[OUTPUT] = str(err)
        return ret_vals

    # default arguments
    port_array: list = arguments.get("ports")
    port_parameters: list = arguments.get("port_parameters")
    options: str = arguments.get("options")
    target: str = arguments.get("target")
    raw_output: bool = arguments.get("raw_output", True)
    timeout: int = arguments.get("timeout", 60)
    # custom command arguments
    format_output: bool = arguments.get(SERIALIZED_OUTPUT, True)
    custom_command: str = arguments.get("command")

    nmap_client = nmap3.Nmap()

    try:
        if custom_command:
            list_of_command_parameters = custom_command.split(" ")
            if format_output:
                list_of_command_parameters = parse_custom_command(list_of_command_parameters)
            output = nmap_client.run_command(cmd=list_of_command_parameters, timeout=timeout)
            xml_root = nmap_client.get_xml_et(output)
            serialized_output = nmap_client.parser.filter_top_ports(xml_root)
        else:
            xml_root = execute_scan(target, options, port_array, nmap_client, timeout)
            serialized_output = nmap_client.parser.filter_top_ports(xml_root)
            output = ElementTree.tostring(xml_root, encoding="unicode")
    except Exception as err:
        ret_vals[OUTPUT] = str(err)
        return ret_vals

    ret_vals[SERIALIZED_OUTPUT] = serialized_output

    if "0 hosts up" in serialized_output["runtime"]["summary"]:
        ret_vals[OUTPUT] = "Provided target is not up or not reachable"
        return ret_vals

    if raw_output:
        ret_vals[OUTPUT] = output

    if port_parameters is not None:
        module_failed = filter_nmap_output_ports(serialized_output, port_parameters)
        if module_failed:
            return ret_vals

    ret_vals[RETURN_CODE] = 0
    return ret_vals

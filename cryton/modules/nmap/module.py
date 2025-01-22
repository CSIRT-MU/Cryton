import re
from xml.etree import ElementTree
import nmap3
from copy import deepcopy

from cryton.lib.utility.module import ModuleBase, ModuleOutput, Result


# TODO: this module is only updated to work with the new rules, it's not reworked
#  - update validation (mainly descriptions)
#  - update check_requirements
#  - rework the module
#  - add tests
class Module(ModuleBase):
    _SCHEMA = {
        "type": "object",
        "description": "Arguments for the `nmap` module.",
        "properties": {
            "timeout": {"type": "integer"},
            "port_parameters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "portid": {"type": "string"},
                        "host": {"type": "string"},
                        "protocol": {"type": "string"},
                        "state": {"type": "string"},
                        "reason": {"type": "string"},
                        "cpe": {"type": "array"},
                        "scripts": {"type": "array"},
                        "service": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "product": {"type": "string"},
                                "version": {"type": "string"},
                                "extrainfo": {"type": "string"},
                                "ostype": {"type": "string"},
                                "method": {"type": "string"},
                                "conf": {"type": "string"},
                            },
                            "additionalProperties": False,
                        },
                    },
                    "additionalProperties": False,
                },
                "description": "",
            },
        },
        "oneOf": [
            {
                "properties": {
                    "target": {"type": "string", "description": "Scan target."},
                    "ports": {"type": "array", "items": {"type": "integer"}, "description": ""},
                    "options": {"type": "string", "description": "Additional nmap parameters."},
                },
                "required": ["target"],
                # "additionalProperties": False  # TODO: solve
            },
            {
                "properties": {
                    "command": {"type": "string", "description": "Command to run (with executable)."},
                    "serialize_output": {"type": "boolean"},
                },
                "required": ["command"],
                # "additionalProperties": False  # TODO: solve
            },
        ],
    }

    def __init__(self, arguments: dict):
        super().__init__(arguments)

    def check_requirements(self) -> None:
        pass

    def execute(self) -> ModuleOutput:
        # default arguments
        port_array: list = self._arguments.get("ports")
        port_parameters: list = self._arguments.get("port_parameters")
        options: str = self._arguments.get("options")
        target: str = self._arguments.get("target")
        raw_output: bool = self._arguments.get("raw_output", True)
        timeout: int = self._arguments.get("timeout", 60)
        # custom command arguments
        custom_command: str = self._arguments.get("command")
        serialize_output: bool = self._arguments.get("serialize_output", True)

        nmap_client = nmap3.Nmap()

        try:
            if custom_command:
                list_of_command_parameters = custom_command.split(" ")
                if serialize_output:
                    list_of_command_parameters = parse_custom_command(list_of_command_parameters)
                output = nmap_client.run_command(cmd=list_of_command_parameters, timeout=timeout)
                xml_root = nmap_client.get_xml_et(output)
                serialized_output = nmap_client.parser.filter_top_ports(xml_root)
            else:
                xml_root = execute_scan(target, options, port_array, nmap_client, timeout)
                serialized_output = nmap_client.parser.filter_top_ports(xml_root)
                output = ElementTree.tostring(xml_root, encoding="unicode")
        except Exception as err:
            self._data.output = str(err)
            return self._data

        self._data.serialized_output = serialized_output

        if "0 hosts up" in serialized_output["runtime"]["summary"]:
            self._data.output = "Provided target is not up or not reachable"
            return self._data

        if raw_output:
            self._data.output = output

        if port_parameters is not None:
            module_failed = filter_nmap_output_ports(serialized_output, port_parameters)
            if module_failed:
                return self._data

        self._data.result = Result.OK

        return self._data


def execute_scan(
    target: str, options: str | None, ports: list | None, nmap_client: nmap3.Nmap, timeout: int
) -> ElementTree.Element:
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
        if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", key):
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

from datetime import datetime
import yaml
import string
import random
import json
from typing import List, Union, Dict  # TODO: replace Dict/List with dict/list
import pytz
import click
import requests

from cryton.cli.config import SETTINGS
from cryton.cli.utility import constants


class CLIContext:
    """
    Context object for CLI. Contains necessary data for link creation.
    """

    def __init__(self, host: str, port: int, ssl: bool, debug: bool):
        self._api_url = f'{"https" if ssl else "http"}://{host}:{port}/api/'
        self.debug = debug

    def _build_request_url(self, endpoint_url: str, object_id: int = None):
        return f"{self._api_url}{endpoint_url if object_id is None else endpoint_url.format(object_id)}"

    def api_delete(self, endpoint_url: str, object_id: int):
        try:
            return requests.delete(self._build_request_url(endpoint_url, object_id))
        except requests.exceptions.ConnectionError:
            return f"Unable to connect."

    def api_get(self, endpoint_url: str, object_id: int = None, parameters: dict = None):
        try:
            return requests.get(self._build_request_url(endpoint_url, object_id), parameters)
        except requests.exceptions.ConnectionError:
            return f"Unable to connect."

    def api_post(
        self, endpoint_url: str, object_id: int = None, data: dict = None, json: dict = None, files: dict = None
    ):
        try:
            return requests.post(self._build_request_url(endpoint_url, object_id), data, json, files=files)
        except requests.exceptions.ConnectionError:
            return f"Unable to connect."

    def get_items(
        self,
        endpoint: str,
        offset: int,
        limit: int,
        additional_parameters: dict[str, Union[str, int]],
        include_fields: list[str],
        less: bool,
        localize: bool,
    ) -> None:
        """
        function for getting listings.
        :param endpoint: The endpoint to use
        :param offset: Initial index from which to return the results
        :param limit: Number of results per page
        :param additional_parameters: Phrase to use to filter the logs
        :param include_fields: List of fields to include in the output
        :param less: Show less like output
        :param localize: If datetime variables should be converted to local timezone
        :return: None
        """
        parameters = {"offset": offset, "limit": limit} | additional_parameters

        response = self.api_get(endpoint, parameters=parameters)
        print_items(response, include_fields, less, localize, self.debug)

    def delete_item(self, endpoint: str, object_id: int) -> None:
        response = self.api_delete(endpoint, object_id)
        print_message(response, self.debug)


class Context(click.Context):
    obj: CLIContext


def save_yaml_to_file(content: dict, file_path: str, file_prefix: str = "file") -> str:
    """
    Save content into file.
    :param file_path: Where to save the file (default is /tmp/prefix_timestamp_tail)
    :param content: What should be saved to the file
    :param file_prefix: Prefix for the file name (only if path is `/tmp`)
    :return: Path to the file
    """
    if file_path == "/tmp":
        time_stamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        file_tail = "".join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=5))
        file_path = f"/tmp/{file_prefix}_{time_stamp}_{file_tail}"

    try:
        with open(file_path, "w+") as report_file:
            yaml.dump(content, report_file, sort_keys=False)
    except IOError as e:
        raise IOError(f"Unable to save file to {file_path}. Original exception: {e}")

    return file_path


def load_files(file_paths: List[str]) -> Dict[str, bytes]:
    """
    Load files from paths.
    :param file_paths: File paths to load
    :return: Loaded files
    """
    files = {}

    for i in range(len(file_paths)):
        with open(file_paths[i], "rb") as f:
            files.update({f"{i}": f.read()})

    return files


def convert_from_utc(utc_str: str) -> datetime:
    """
    Convert datetime in UTC timezone to specified timezone
    :param utc_str: datetime in UTC timezone to convert
    :return: datetime with the specified timezone
    """
    try:
        utc_datetime = datetime.strptime(utc_str, constants.TIME_FORMAT)
    except ValueError:
        utc_datetime = datetime.strptime(utc_str, constants.TIME_DETAILED_FORMAT)

    if not utc_datetime.tzinfo:
        utc_datetime = pytz.utc.localize(utc_datetime, is_dst=None)
    new_datetime = utc_datetime.astimezone(pytz.timezone(SETTINGS.timezone))

    return new_datetime.replace(tzinfo=None)


def parse_response(response: requests.Response) -> Union[str, dict]:
    """
    Parse the response to the desired format.
    :param response: Response containing data from REST API
    :return: Parsed response
    """
    try:
        response_data = response.json()
    except json.JSONDecodeError:
        if response.text == "":
            return "Empty response."
        return "Unable to parse response details."

    if isinstance(response_data, list):  # ValidationError can return multiple errors at once
        detailed_msg = "\n\n ".join(response_data)
    elif (results := response_data.get("results")) is not None:
        detailed_msg = results
    elif (detail := response_data.get("detail")) is not None and len(response_data) == 1:
        detailed_msg = detail
    else:
        detailed_msg = response_data

    return detailed_msg


def print_message(response: Union[str, requests.Response], debug: bool = False) -> bool:
    """
    Echo message containing information about success or failure of user's request.
    :param response: Response containing data from REST API
    :param debug: Show non formatted raw output
    :return: True if the response is valid or unable to decide
    """
    if isinstance(response, str):
        click.secho(response, fg="red")
        return False

    if debug:
        click.echo(response.text)
        return True

    parsed_response = parse_response(response)
    if not response.ok:
        click.echo(f"{click.style(parsed_response, fg='red')} ({response.reason})")
        return False
    else:
        click.echo(f"{click.style('Success!', fg='green')} ({parsed_response})")
        return True


def format_result_line(line: dict, to_print: List[str], localize: bool) -> str:
    """
    Filter dictionary values, optionally update timezone, and create user readable line.
    :param line: dictionary that should be parsed
    :param to_print: Keys to be shown (printed out)
    :param localize: If datetime variables should be converted to local timezone
    :return: Filtered and localized string
    """
    if not to_print:
        return ", ".join([f"{key}: {value}" for key, value in line.items()])

    line_to_print = ""
    datetime_variables = ["finish_time", "pause_time", "start_time", "created_at", "updated_at", "schedule_time"]

    for key in to_print:
        value = line.get(key)

        if localize and value is not None and key in datetime_variables:
            value = convert_from_utc(value)

        if line_to_print != "":
            line_to_print += ", "
        line_to_print += f"{key}: {value}"

    return line_to_print


def format_list_results(results: list, to_print: List[str], localize: bool) -> list:
    """
    Format list response to be user readable.
    :param results: Results from API
    :param to_print: Parameters to be shown (printed out)
    :param localize: If datetime variables should be converted to local timezone
    :return: Formatted list
    """
    length = len(results)
    parsed_results = []
    for i in range(length):
        line = format_result_line(results[i], to_print, localize)
        if length != 0 and i < length - 1:
            line += "\n\n"

        parsed_results.append(line)

    return parsed_results


def print_items(
    response: Union[str, requests.Response],
    to_print: List[str],
    less: bool = False,
    localize: bool = False,
    debug: bool = False,
) -> None:
    """
    Remove ignored parameters and echo the rest.
    :param response: Response containing data from REST API
    :param to_print: Parameters to be shown (printed out)
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :param debug: Show non formatted raw output
    :return: None
    """
    if isinstance(response, str):
        click.secho(response, fg="red")
        return

    if debug:
        click.echo(response.text)
        return

    parsed_response = parse_response(response)
    if not response.ok:
        click.echo(f"{click.style(parsed_response, fg='red')} ({response.reason})")
    else:
        if not isinstance(parsed_response, list):
            parsed_response = [parsed_response]

        parsed_results = format_list_results(parsed_response, to_print, localize)
        if not parsed_results:
            click.secho("No matching objects...", fg="green")
        else:
            if less:
                click.echo_via_pager(parsed_results)
            else:
                for line in parsed_results:
                    click.echo(line)


def format_report(run: dict, localize: bool):
    """
    Go through each iterable in report and do the following:
      - localize it, if it is a datetime variable
    :param run: Element in which we want to change values
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    datetime_variables = ["finish_time", "pause_time", "start_time", "created_at", "updated_at", "schedule_time"]

    run_changes = {}
    for key, value in run.items():
        if localize and value is not None and key in datetime_variables:
            run_changes[key] = convert_from_utc(value)

    run.update(run_changes)

    plan_changes = {}
    for plan in run["plan_executions"]:
        for key, value in plan.items():
            if localize and value is not None and key in datetime_variables:
                plan_changes[key] = convert_from_utc(value)

        plan.update(plan_changes)

        stage_changes = {}
        for stage in plan["stage_executions"]:
            for key, value in stage.items():
                if localize and value is not None and key in datetime_variables:
                    stage_changes[key] = convert_from_utc(value)

            stage.update(stage_changes)

            step_changes = {}
            for step in stage["step_executions"]:
                for key, value in step.items():
                    if localize and value is not None and key in datetime_variables:
                        step_changes[key] = convert_from_utc(value)

                step.update(step_changes)

    return run


def save_yaml(
    response: Union[str, requests.Response],
    file_path: str,
    file_name: str,
    echo_only: bool = False,
    less: bool = False,
    localize: bool = False,
    debug: bool = False,
) -> None:
    """
    Get yaml and save/echo it.
    :param response: Response containing data from REST API
    :param file_path: Where to save the file
    :param file_name: Prefix for the file name (only if path is `/tmp`)
    :param echo_only: If the report should be only printed out and not saved
    :param less: Show less like output
    :param debug: Show non formatted raw output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    if isinstance(response, str):
        click.secho(response, fg="red")
        return

    if debug:
        click.echo(response.text)
        return

    parsed_response = parse_response(response)
    if not response.ok:
        click.echo(f"{click.style(parsed_response, fg='red')} ({response.reason})")
    else:
        if localize:
            format_report(parsed_response, localize)

        if not echo_only:
            try:
                path_to_file = save_yaml_to_file(parsed_response, file_path, file_name)
            except IOError as ex:
                click.secho(f"{ex}", fg="red")
            else:
                click.secho(f"Successfully saved file to {path_to_file}", fg="green")

        else:
            if less:
                click.echo_via_pager(yaml.dump(parsed_response, sort_keys=False))
            else:
                click.echo(yaml.dump(parsed_response, sort_keys=False))


def render_documentation(raw_documentation: dict, layer: int) -> str:
    """
    Process and create documentation in markdown.
    :param raw_documentation: Unprocessed documentation
    :param layer: Header level
    :return: Documentation in Markdown
    """
    # Create header
    doc = f"{'#' * layer} {raw_documentation.get('name')}\n"

    # Create help text
    help_text = ""
    for line in raw_documentation.get("help").split("\x0c")[0].split("\n"):
        if new_line := line.lstrip().rstrip():
            help_text += f"{new_line}\n\n"

    doc += f"{help_text}"

    # Prepare arguments and options
    arguments, options = [], []
    for parameter in raw_documentation.get("params"):
        arguments.append(parameter) if "argument" in parameter.get("param_type_name") else options.append(parameter)

    # Generate arguments for command
    if arguments:
        doc += "**Arguments:**  \n"
        for argument in arguments:
            doc += f"- {argument.get('name').upper()}  \n"

    # Generate options for command
    doc += "\n**Options:**  \n"
    for option in options:
        opts = option.get("opts")
        parsed_opts = f"`{opts[0]}`, `{opts[1]}`" if len(opts) != 1 else f"`{opts[0]}`"
        doc += f"- {option.get('name')} ({parsed_opts}) - {option.get('help')}  \n"

    doc += "\n"
    # Generate documentation for sub commands
    if raw_documentation.get("commands") is not None:
        for cmd_detail in raw_documentation.get("commands").values():
            doc += render_documentation(cmd_detail, layer + 1)

    return doc


def clean_up_documentation(documentation: str) -> str:
    """
    Remove forbidden characters from documentation.
    :param documentation: Human-readable documentation
    :return: Clean documentation
    """
    return documentation.replace("_", r"\_")

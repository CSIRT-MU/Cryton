from threading import Thread
from functools import reduce
from datetime import datetime, timedelta
import pytz
import amqpstorm
import re
import json

from cryton.hive.config.settings import SETTINGS
from cryton.hive.utility import exceptions, logger

from django.utils import timezone


def convert_to_utc(original_datetime: datetime, time_zone: str = "utc", offset_aware: bool = False) -> datetime:
    """
    Convert datetime in specified timezone to UTC timezone
    :param original_datetime: datetime to convert
    :param time_zone: timezone of the original datetime (examples: "utc"; "Europe/Prague")
    :param offset_aware: if True, utc_datetime will be offset-aware, else it will be offset-naive
    :return: datetime in UTC timezone
    """
    if not original_datetime.tzinfo:
        original_datetime = pytz.timezone(time_zone).localize(original_datetime, is_dst=None)
        # original_datetime = original_datetime.astimezone(time_zone)

    utc_datetime = original_datetime.astimezone(timezone.utc)
    if not offset_aware:
        return utc_datetime.replace(tzinfo=None)
    return utc_datetime


def convert_from_utc(utc_datetime: datetime, time_zone: str, offset_aware: bool = False) -> datetime:
    """
    Convert datetime in UTC timezone to specified timezone
    :param utc_datetime: datetime in UTC timezone to convert
    :param time_zone: timezone of the new datetime (examples: "utc"; "Europe/Prague")
    :param offset_aware: if True, utc_datetime will be offset-aware, else it will be offset-naive
    :return: datetime with the specified timezone
    """
    if not utc_datetime.tzinfo:
        utc_datetime = pytz.utc.localize(utc_datetime, is_dst=None)

    new_datetime = utc_datetime.astimezone(pytz.timezone(time_zone))
    if not offset_aware:
        return new_datetime.replace(tzinfo=None)
    return new_datetime


def parse_delta_to_datetime(delta: str) -> timedelta:
    try:
        delta_split = delta.split(":")
        return timedelta(hours=int(delta_split[0]), minutes=int(delta_split[1]), seconds=int(delta_split[2]))
    except Exception:
        raise exceptions.UserInputError("Invalid delta provided. Correct format is [hours]:[minutes]:[seconds].", delta)


def split_into_lists(input_list: list, target_number_of_lists: int) -> list[list]:
    """
    Evenly splits list into n lists.
    E.g. split_into_lists([1,2,3,4], 4) returns [[1], [2], [3], [4]].
    :param input_list: object to split
    :param target_number_of_lists: how many lists to split into
    :returns: list of lists containing original items
    """
    quotient, reminder = divmod(len(input_list), target_number_of_lists)
    return [
        input_list[i * quotient + min(i, reminder) : (i + 1) * quotient + min(i + 1, reminder)]
        for i in range(target_number_of_lists)
    ]


def run_executions_in_threads(step_executions: list) -> None:
    """
    Creates new Rabbit connection, distributes step executions into threads and runs the threads.
    To set desired number of threads/process, see "CRYTON_HIVE_EXECUTION_THREADS_PER_PROCESS" variable in config.

    :param step_executions: list of step execution objects
    """
    connection_parameters = {
        "hostname": SETTINGS.rabbit.host,
        "username": SETTINGS.rabbit.username,
        "password": SETTINGS.rabbit.password,
        "port": SETTINGS.rabbit.port,
    }
    with amqpstorm.Connection(**connection_parameters) as connection:
        # Split executions into threads
        thread_lists = split_into_lists(step_executions, SETTINGS.threads_per_process)
        threads = []
        for thread_step_executions in thread_lists:
            new_thread = Thread(target=run_step_executions, args=(connection, thread_step_executions))
            threads.append(new_thread)

        for thread in threads:
            thread.start()

        # Wait for threads to finish
        for thread in threads:
            thread.join()


def run_step_executions(rabbit_connection: amqpstorm.Connection, step_execution_list: list) -> None:
    """
    Creates new Rabbit channel and runs step executions.

    :param rabbit_connection: Rabbit connection
    :param step_execution_list: list of step execution objects to execute
    """
    with rabbit_connection.channel() as channel:
        for step_execution in step_execution_list:
            logger.logger.debug("Running Step Execution in thread", step_execution_id=step_execution.model.id)
            step_execution.start(channel)


def getitem(obj: list | dict, key: str):
    """
    Get item from object using key.
    :param obj: Iterable accessible using key
    :param key: Key to use to get (match) Item
    :return: Matched item
    """
    match = re.match(r"^\[[0-9]+]$", key)  # Check if key matches List index.
    if match is not None:
        key = int(match.group()[1:-1])  # Convert List index to int.

    result = None
    if isinstance(key, str) and isinstance(obj, dict):  # Use key to get item from Dict.
        result = obj.get(key)
        if result is None and key.isdigit():  # May be int.
            result = obj.get(int(key))
    elif isinstance(key, int) and isinstance(obj, list):  # Use key to get item from List.
        try:
            result = obj[key]
        except IndexError:
            pass
    return result


def parse_dot_argument(dot_argument: str) -> list[str]:
    """
    Takes a single argument (Dict key) from dot notation and checks if it also contains list indexes.
    :param dot_argument: Dict key from dot notation possibly containing list indexes
    :return: Dict key and possible List indexes
    """
    list_indexes = re.search(r"((\[[0-9]+])+$)", dot_argument)  # Check for List indexes at the argument's end.
    if list_indexes is not None:  # Get each List index in '[index]' format and get index only.
        parsed_list_indexes = re.findall(r"(\[[0-9]+])", list_indexes.group())
        parsed_list_indexes = [index for index in parsed_list_indexes]
        return [dot_argument[0 : list_indexes.start()]] + parsed_list_indexes
    return [dot_argument]  # If no List Indexes are present.


def get_from_dict(dict_in: dict, value: str, separator: str):
    """
    Get value from dict_in dict
    eg:
      dict_in: {'output': {'username': 'admin'}}
      value: '$dict_in.output.username'
      return: 'admin'
    :param value: value defined in template
    :param dict_in: dict_in for this step
    :param separator: separator for dynamic variable
    :return: value from dict_in
    """
    dynamic_var_arguments = value.lstrip("$").split(separator)  # Get keys using '.' separator.
    all_args = []  # Dict keys and List indexes.
    for argument in dynamic_var_arguments:  # Go through dot_args and separate all args.
        all_args.extend(parse_dot_argument(argument))

    try:
        res = reduce(getitem, all_args, dict_in)
    except KeyError:
        res = None

    return res


def _finditem(obj, key):
    """
    Check if giben key exists in an object
    :param obj: dictionary/list
    :param key: key
    :return: value at the key position
    """
    if key in obj:
        return obj[key]
    for k, v in obj.items():
        if isinstance(v, dict):
            item = _finditem(v, key)
            if item is not None:
                return item


def fill_dynamic_variables(dict_to_update: dict, dynamic_variables_dict: dict, separator: str, startswith: str = "$"):
    """

    Fill variables in dict_to_update with dynamic_variables_dict.

    :param dict_to_update: Module arguments that should be filled with dynamic variables
    :param dynamic_variables_dict: Output from another module that will be used to update 'dict_to_update'
    :param startswith: prefix, eg. $
    :param separator: separator for dynamic variable
    :return:
    """

    if isinstance(dict_to_update, dict):
        for argument_key, argument_value in dict_to_update.items():
            if isinstance(argument_value, str):
                if argument_value.startswith(startswith):
                    new_val = get_from_dict(dynamic_variables_dict, argument_value, separator)
                    if new_val is not None:
                        dict_to_update.update({argument_key: new_val})
            elif isinstance(argument_value, dict):
                fill_dynamic_variables(argument_value, dynamic_variables_dict, separator, startswith)
            elif isinstance(argument_value, list):
                for list_value in argument_value:
                    fill_dynamic_variables(list_value, dynamic_variables_dict, separator, startswith)

    return dict_to_update


def get_all_values(input_container):
    """
    Get all values (recursively) from a dict
    :param input_container: input dict or list
    :return: yields elements, use as list(get_all_values(d))
    """
    if isinstance(input_container, dict):
        for value in input_container.values():
            yield from get_all_values(value)
    elif isinstance(input_container, list):
        for item in input_container:
            yield from get_all_values(item)
    else:
        yield input_container


def get_dynamic_variables(in_dict, prefix="$"):
    """
    Get list of dynamic variables for input dict
    :param in_dict:
    :param prefix:
    :return:
    """
    vars_list = list(get_all_values(in_dict))

    for i in vars_list:
        if isinstance(i, str) and i.startswith(prefix):
            yield i


def get_prefixes(vars_list: list, separator: str):
    """
    Get list of prefixes from list of dynamic variables
    :param vars_list: Individual pieces of a dynamic variable
    :param separator: Dynamic variable separator
    :return:
    """
    for i in vars_list:
        yield i.split(separator)[0].lstrip("$")


def pop_key(in_dict, val):
    """
    Pop key at specified position (eg. 'k1.k2.k3')
    :param in_dict:
    :param val:
    :return: Nothing, changes in_dict inplace
    """
    if type(in_dict) != dict:
        return in_dict
    if type(val) == list and len(val) > 1:
        if len(val) != 2:
            return pop_key(in_dict.get(val[0]), val[1:])
        else:
            return in_dict.get(val[0]).pop(val[1])
    else:
        print(val)
        return in_dict.pop(val[0])


def add_key(in_dict, path, val):
    """
    Add value on specified key position
    :param in_dict: eg. {a: 1, b:2}
    :param path: 'c.d.e'
    :param val: '3
    :return: changes in place, eg. {a:1, b:2, c:{d:{e:3}}}
    """
    first = True
    tmp_dict = {}

    for i in path.split(".")[::-1]:
        if first is True:
            tmp_dict = {i: val}
            first = False
        else:
            tmp_dict = {i: tmp_dict}
    in_dict.update(tmp_dict)


def rename_key(in_dict, rename_from, rename_to):
    """
    Rename key (= move to different place)

    eg.
    in_dict = {a: 1, b: 2, c: {d: 3}}
    rename_from = 'c.d'
    rename_to = 'e.f.g'

    result = {a: 1, b: 2, e: {f: {g: 3}}}

    :param in_dict:
    :param rename_from:
    :param rename_to:
    :return: Changes inplace
    :raises KeyError, if rename_from key is not found
    """
    new_val = pop_key(in_dict, rename_from.split("."))
    add_key(in_dict, rename_to, new_val)


def get_logs(offset: int, limit: int, filter_params: dict[str, str]) -> list[dict[str, str]]:
    """
    Get and parse logs from log file.
    :param offset: On what line to start reading logs
    :param limit: Maximum number of logs to return
    :param filter_params: Substrings used for filtering the logs
    :return: Parsed Logs
    """
    log_file_path = SETTINGS.log_file
    logs = []
    with open(log_file_path, "r") as log_file:
        raw_logs = log_file.readlines()

    number_of_logs = len(raw_logs)

    if limit == 0:
        limit = number_of_logs

    for i in range(offset, number_of_logs):
        raw_log = raw_logs[i]
        try:
            parsed_log = json.loads(raw_log)
        except json.JSONDecodeError:  # TODO: make sure this won't happen and remove
            parsed_log = {"detail": raw_log.rstrip("\n").rstrip(" ").lstrip(" ")}

        if not all(value in parsed_log.get(key, "") for key, value in filter_params.items()):
            continue

        logs.append(parsed_log)

        if len(logs) == limit:
            break

    return logs

import click
from typing import Union

from cryton.cli.utility import helpers
from cryton.cli.utility.decorators import *
from cryton.cli.config import Log


@click.group("logs")
@click.pass_context
def log(_) -> None:
    """
    Manage logs from here.

    \f
    :param _: Click context
    :return: None
    """


@log.command("list")
@click.pass_context
@common_list_decorators
def log_list(
    ctx: helpers.Context,
    less: bool,
    offset: int,
    limit: int,
    localize: bool,
    parameter_filters: tuple[tuple[str, Union[str, int]]],
) -> None:
    """
    List existing Logs.

    \f
    :param ctx: Click context
    :param less: Show less like output
    :param offset: Initial index from which to return the results
    :param limit: Number of results per page
    :param localize: If datetime variables should be converted to local timezone
    :param parameter_filters: Filter results using returned parameters
    :return: None
    """
    additional_parameters = {each[0]: each[1] for each in parameter_filters}
    ctx.obj.get_items(Log.LIST, offset, limit, additional_parameters, [], less, localize)

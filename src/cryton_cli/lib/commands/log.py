import click
from typing import Optional, List

from cryton_cli.lib.util import api, util


# Worker
@click.group('logs')
@click.pass_context
def log(_) -> None:
    """
    Manage logs from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@log.command('list')
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('-o', '--offset', type=click.INT, default=0, help='The initial index from which to return the results.')
@click.option('-l', '--limit', type=click.INT, default=20, help='Number of results to return per page.')
@click.option('-f', '--filter', 'parameter_filters', type=click.STRING, multiple=True,
              help='Filter results using substrings (for example `warning`, `2023-08-11T13:26`, etc.).')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.pass_context
def log_list(ctx: click.Context, less: bool, offset: int, limit: int, localize: bool,
             parameter_filters: Optional[List[str]]) -> None:
    """
    List existing Logs in Cryton.

    \f
    :param ctx: Click ctx object
    :param less: Show less like output
    :param offset: Initial index from which to return the results
    :param limit: Number of results per page
    :param localize: If datetime variables should be converted to local timezone
    :param parameter_filters: Phrase to use to filter the logs
    :return: None
    """
    appendix = f'?limit={limit}&offset={offset}'
    if parameter_filters is not None:
        appendix += f'&filter={"|".join(parameter_filters)}'
    response = api.get_request(ctx.obj.api_url, api.LOG_LIST + appendix)

    to_print = []
    util.echo_list(response, to_print, less, localize, ctx.obj.debug)

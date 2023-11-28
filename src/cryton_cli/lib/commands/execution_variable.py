import click
from typing import List, Optional

from cryton_cli.lib.util import api, util


# Execution variables
@click.group('execution-variables')
@click.pass_context
def execution_variable(_) -> None:
    """
    Manage Execution variables from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@execution_variable.command('list')
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('-o', '--offset', type=click.INT, default=0, help='The initial index from which to return the results.')
@click.option('-l', '--limit', type=click.INT, default=20, help='Number of results to return per page.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.option('-p', '--parent', type=click.INT, help='Filter Execution variables using Plan execution ID.')
@click.option('-f', '--filter', 'parameter_filters', type=click.STRING, multiple=True,
              help='Filter results using returned parameters (for example `id=1`, `name=test`, etc.).')
@click.pass_context
def execution_variable_list(ctx: click.Context, less: bool, offset: int, limit: int, localize: bool,
                            parent: int, parameter_filters: Optional[List[str]]) -> None:
    """
    List existing Execution variables in Cryton.

    \f
    :param ctx: Click ctx object
    :param less: Show less like output
    :param offset: Initial index from which to return the results
    :param limit: Number of results per page
    :param localize: If datetime variables should be converted to local timezone
    :param parent: Plan execution ID used to filter returned Execution variables
    :param parameter_filters: Filter results using returned parameters (for example `id`, `name`, etc.)
    :return: None
    """
    results_filter = "&".join(parameter_filters)
    appendix = f'?limit={limit}&offset={offset}&{results_filter}'
    custom_params = {}
    if parent is not None:
        custom_params.update({'plan_execution_id': parent})
    response = api.get_request(ctx.obj.api_url, api.EXECUTION_VARIABLE_LIST + appendix, custom_params=custom_params)

    to_print = ['id', 'name', 'value', 'plan_execution']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@execution_variable.command('create')
@click.argument('plan_execution_id', type=click.INT, required=True)
@click.argument('file', type=click.Path(exists=True), required=True, nargs=-1)
@click.pass_context
def execution_variable_create(ctx: click.Context, plan_execution_id: int, file: str) -> None:
    """
    Create new execution variable(s) for PLAN_EXECUTION_ID from FILE.

    PLAN_EXECUTION_ID IS ID of the desired PlanExecution.

    FILE is path (can be multiple) to file(s) containing execution variables.

    \f
    :param ctx: Click ctx object
    :param plan_execution_id: ID of the desired PlanExecution.
    :param file: Path(s) to file(s) containing execution variables.
    :return: None
    """
    files = {}
    for i in range(len(file)):
        files.update({f"{i}": open(file[i], "rb")})
    data = {'plan_execution_id': plan_execution_id}
    response = api.post_request(ctx.obj.api_url, api.EXECUTION_VARIABLE_CREATE, files=files, data=data)

    util.echo_msg(response, 'Execution variable(s) successfully created!', ctx.obj.debug)


@execution_variable.command('show')
@click.argument('execution_variable_id', type=click.INT, required=True)
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.pass_context
def execution_variable_read(ctx: click.Context, execution_variable_id: int, less: bool, localize: bool) -> None:
    """
    Show Execution variable with EXECUTION_VARIABLE_ID saved in Cryton.

    EXECUTION_VARIABLE_ID is ID of the Execution variable you want to see.

    \f
    :param ctx: Click ctx object
    :param execution_variable_id: ID of the desired execution variable
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = api.get_request(ctx.obj.api_url, api.EXECUTION_VARIABLE_READ, execution_variable_id)

    to_print = ['id', 'name', 'value', 'plan_execution']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@execution_variable.command('delete')
@click.argument('execution_variable_id', type=click.INT, required=True)
@click.pass_context
def execution_variable_delete(ctx: click.Context, execution_variable_id: int) -> None:
    """
    Delete Execution variable with EXECUTION_VARIABLE_ID saved in Cryton.

    EXECUTION_VARIABLE_ID is ID of the Execution_variable you want to delete.

    \f
    :param ctx: Click ctx object
    :param execution_variable_id: ID of the desired execution variable
    :return: None
    """
    response = api.delete_request(ctx.obj.api_url, api.EXECUTION_VARIABLE_DELETE, execution_variable_id)

    util.echo_msg(response, 'Execution variable successfully deleted!', ctx.obj.debug)

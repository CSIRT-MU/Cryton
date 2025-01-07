import click

from cryton.cli.utility import helpers
from cryton.cli.utility.decorators import *
from cryton.cli.config import ExecutionVariable


@click.group("execution-variables", helpers.AliasedGroup)
@click.pass_context
def execution_variable(_) -> None:
    """
    Manage Execution variables from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@execution_variable.command("list")
@click.pass_context
@common_list_decorators
@click.option("-p", "--parent", type=click.INT, help="Filter Execution variables using Plan execution ID.")
def execution_variable_list(
    ctx: helpers.Context,
    less: bool,
    offset: int,
    limit: int,
    localize: bool,
    parameter_filters: tuple[tuple[str, str | int]],
    parent: int,
) -> None:
    """
    List existing execution variables.

    \f
    :param ctx: Click ctx object
    :param less: Show less like output
    :param offset: Initial index from which to return the results
    :param limit: Number of results per page
    :param localize: If datetime variables should be converted to local timezone
    :param parameter_filters: Filter results using returned parameters
    :param parent: Plan execution ID used to filter returned Execution variables
    :return: None
    """
    additional_parameters = {each[0]: each[1] for each in parameter_filters}
    if parent is not None:
        additional_parameters["plan_execution_id"] = parent
    include = ["id", "name", "value", "plan_execution"]
    ctx.obj.get_items(ExecutionVariable.LIST, offset, limit, additional_parameters, include, less, localize)


@execution_variable.command("create")
@click.pass_context
@click.argument("plan_execution_id", type=click.INT, required=True)
@click.argument("file", type=click.Path(exists=True), required=True, nargs=-1)
def execution_variable_create(ctx: helpers.Context, plan_execution_id: int, file: str) -> None:
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
    data = {"plan_execution_id": plan_execution_id}
    files = {str(i): open(file[i], "rb") for i in range(len(file))}
    response = ctx.obj.api_post(ExecutionVariable.CREATE, data=data, files=files)
    helpers.print_message(response, ctx.obj.debug)


@execution_variable.command("show")
@click.pass_context
@click.argument("execution_variable_id", type=click.INT, required=True)
@click.option("--less", is_flag=True, help="Show less like output.")
@click.option("--localize", is_flag=True, help="Convert UTC datetime to local timezone.")
def execution_variable_read(ctx: helpers.Context, execution_variable_id: int, less: bool, localize: bool) -> None:
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
    response = ctx.obj.api_get(ExecutionVariable.READ, execution_variable_id)
    include = ["id", "name", "value", "plan_execution"]
    helpers.print_items(response, include, less, localize, ctx.obj.debug)


@execution_variable.command("delete")
@click.pass_context
@click.argument("execution_variable_id", type=click.INT, required=True)
def execution_variable_delete(ctx: helpers.Context, execution_variable_id: int) -> None:
    """
    Delete Execution variable with EXECUTION_VARIABLE_ID saved in Cryton.

    EXECUTION_VARIABLE_ID is ID of the Execution_variable you want to delete.

    \f
    :param ctx: Click ctx object
    :param execution_variable_id: ID of the desired execution variable
    :return: None
    """
    ctx.obj.delete_item(ExecutionVariable.DELETE, execution_variable_id)

import click

from cryton.cli.utility import helpers
from cryton.cli.utility.decorators import *
from cryton.cli.config import Stage, StageExecution


@click.group("stages")
@click.pass_context
def stage(_) -> None:
    """
    Manage Stages from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@stage.command("list")
@click.pass_context
@common_list_decorators
@click.option("-p", "--parent", type=click.INT, help="Filter Stages using Plan ID.")
def stage_list(
    ctx: helpers.Context,
    less: bool,
    offset: int,
    limit: int,
    localize: bool,
    parameter_filters: tuple[tuple[str, str | int]],
    parent: int,
) -> None:
    """
    List existing Stages in Cryton.

    \f
    :param ctx: Click ctx object
    :param less: Show less like output
    :param offset: Initial index from which to return the results
    :param limit: Number of results per page
    :param localize: If datetime variables should be converted to local timezone
    :param parent: Plan ID used to filter returned Stages
    :param parameter_filters: Filter results using returned parameters
    :return: None
    """
    additional_parameters = {each[0]: each[1] for each in parameter_filters}
    if parent is not None:
        additional_parameters["plan_id"] = parent
    include = ["id", "name", "metadata", "type", "arguments"]
    ctx.obj.get_items(Stage.LIST, offset, limit, additional_parameters, include, less, localize)


@stage.command("create")
@click.pass_context
@click.argument("plan_id", type=click.INT, required=True)
@click.argument("file", type=click.Path(exists=True), required=True)
@click.option(
    "-i",
    "--inventory-file",
    "inventory_files",
    type=click.Path(exists=True),
    multiple=True,
    help="Inventory file used to fill the template. Can be used multiple times.",
)
def stage_create(ctx: helpers.Context, plan_id: int, file: str, inventory_files: list) -> None:
    """
    Create Stage from FILE and add it to Plan with PLAN_ID.

    PLAN_ID is an ID of the Plan you want to add the Stage to.
    FILE is a path to the file containing the Stage template.

    \f
    :param ctx: Click ctx object
    :param plan_id: ID of the Plan to use
    :param file: File used as the Stage template
    :param inventory_files: Inventory file(s) used to fill the template
    :return: None
    """
    data = {"plan_id": plan_id}
    files = helpers.load_files(inventory_files)
    with open(file, "rb") as f:
        files["file"] = f.read()
    response = ctx.obj.api_post(Stage.CREATE, data=data, files=files)
    helpers.print_message(response, ctx.obj.debug)


@stage.command("show")
@click.pass_context
@click.argument("stage_id", type=click.INT, required=True)
@d_less
@d_localize
def stage_read(ctx: helpers.Context, stage_id: int, less: bool, localize: bool) -> None:
    """
    Show Stage with STAGE_ID.

    STAGE_ID is ID of the Stage you want to see.

    \f
    :param ctx: Click ctx object
    :param stage_id: ID of the desired Stage
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(Stage.READ, stage_id)
    include = ["id", "name", "metadata", "type", "arguments"]
    helpers.print_items(response, include, less, localize, ctx.obj.debug)


@stage.command("delete")
@click.pass_context
@click.argument("stage_id", type=click.INT, required=True)
def stage_delete(ctx: helpers.Context, stage_id: int) -> None:
    """
    Delete Stage with STAGE_ID.

    STAGE_ID is ID of the Stage you want to delete.

    \f
    :param ctx: Click ctx object
    :param stage_id: ID of the desired Stage
    :return: None
    """
    ctx.obj.delete_item(Stage.DELETE, stage_id)


@stage.command("validate")
@click.pass_context
@click.argument("file", type=click.Path(exists=True), required=True)
@click.argument("plan_id", type=click.INT, required=True)
@click.option(
    "-i",
    "--inventory-file",
    "inventory_files",
    type=click.Path(exists=True),
    multiple=True,
    help="Inventory file used to fill the template. Can be used multiple times.",
)
def stage_validate(ctx: helpers.Context, file: str, plan_id: int, inventory_files: list) -> None:
    """
    Validate FILE containing stage against a plan with PLAN_ID.

    FILE is path/to/your/file that you want to validate.
    PLAN_ID is an ID of the plan you want to validate the stage against.

    \f
    :param ctx: Click ctx object
    :param plan_id: ID of the Plan to use
    :param file: File containing your Stage in yaml
    :param inventory_files: Inventory file(s) used to fill the template
    :return: None
    """
    data = {"plan_id": plan_id}
    files = helpers.load_files(inventory_files)
    with open(file, "rb") as f:
        files["file"] = f.read()
    response = ctx.obj.api_post(Stage.VALIDATE, data=data, files=files)
    helpers.print_message(response, ctx.obj.debug)


@stage.command("start-trigger")
@click.pass_context
@click.argument("stage_id", type=click.INT, required=True)
@click.argument("plan_execution_id", type=click.INT, required=True)
def stage_start_trigger(ctx: helpers.Context, stage_id: int, plan_execution_id: int) -> None:
    """
    Start Stage's trigger with STAGE_ID under Plan execution with PLAN_EXECUTION_ID.

    STAGE_ID is an ID of the Stage you want to start.
    PLAN_EXECUTION_ID is an ID of the Plan execution you want to set as a parent of the Stage execution.

    \f
    :param ctx: Click ctx object
    :param stage_id: ID of the Stage that will be used to create execution
    :param plan_execution_id: ID of the Plan execution that will be set as a parent of the Stage execution
    :return: None
    """
    arguments = {"plan_execution_id": plan_execution_id}
    response = ctx.obj.api_post(Stage.START_TRIGGER, stage_id, json=arguments)
    helpers.print_message(response, ctx.obj.debug)


@click.group("stage-executions")
@click.pass_context
def stage_execution(_) -> None:
    """
    Manage Stage's executions from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@stage_execution.command("list")
@click.pass_context
@common_list_decorators
@click.option("-p", "--parent", type=click.INT, help="Filter Stage executions using Plan execution ID.")
def stage_execution_list(
    ctx: helpers.Context,
    less: bool,
    offset: int,
    limit: int,
    localize: bool,
    parameter_filters: tuple[tuple[str, str | int]],
    parent: int,
) -> None:
    """
    List existing Stage's executions in Cryton.

    \f
    :param ctx: Click ctx object
    :param less: Show less like output
    :param offset: Initial index from which to return the results
    :param limit: Number of results per page
    :param localize: If datetime variables should be converted to local timezone
    :param parent: Plan execution ID used to filter returned Stage executions
    :param parameter_filters: Filter results using returned parameters (for example `id`, `name`, etc.)
    :return: None
    """
    additional_parameters = {each[0]: each[1] for each in parameter_filters}
    if parent is not None:
        additional_parameters["plan_execution_id"] = parent
    include = ["id", "schedule_time", "start_time", "pause_time", "finish_time", "state"]
    ctx.obj.get_items(StageExecution.LIST, offset, limit, additional_parameters, include, less, localize)


@stage_execution.command("delete")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
def stage_execution_delete(ctx: helpers.Context, execution_id: int) -> None:
    """
    Delete Stage's execution with EXECUTION_ID.

    EXECUTION_ID is ID of the Stage's execution you want to delete.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Stage's execution
    :return: None
    """
    ctx.obj.delete_item(StageExecution.DELETE, execution_id)


@stage_execution.command("show")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
@d_less
@d_localize
def stage_execution_read(ctx: helpers.Context, execution_id: int, less: bool, localize: bool) -> None:
    """
    Show Stage's execution with EXECUTION_ID.

    EXECUTION_ID is ID of the Stage's execution you want to see.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Stage's execution
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(StageExecution.READ, execution_id)
    include = ["id", "schedule_time", "start_time", "pause_time", "finish_time", "state"]
    helpers.print_items(response, include, less, localize, ctx.obj.debug)


@stage_execution.command("report")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
@d_save_report
@d_less
@d_localize
def stage_execution_report(ctx: helpers.Context, execution_id: int, file: str, less: bool, localize: bool) -> None:
    """
    Create report for Stage's execution with EXECUTION_ID.

    EXECUTION_ID is ID of the Stage's execution you want to create report for.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Stage's execution
    :param file: File to save the report to
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(StageExecution.REPORT, execution_id)
    helpers.save_yaml(response, file, f"stage-execution-{execution_id}.yml", less, less, localize, ctx.obj.debug)


@stage_execution.command("stop")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
def stage_execution_stop(ctx: helpers.Context, execution_id: int) -> None:
    """
    Stop Stage's execution with EXECUTION_ID.

    EXECUTION_ID is ID of the Stage's execution you want to stop.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Stage's execution
    :return: None
    """
    response = ctx.obj.api_post(StageExecution.STOP, execution_id)
    helpers.print_message(response, ctx.obj.debug)


@stage_execution.command("re-execute")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
@click.option("--immediately", is_flag=True, help="Re-execute StageExecution immediately without starting its Trigger.")
def stage_execution_re_execute(ctx: helpers.Context, execution_id: int, immediately: bool) -> None:
    """
    Re-execute Stage's execution with EXECUTION_ID.

    EXECUTION_ID is ID of the Stage's execution you want to stop.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Stage's execution
    :param immediately: True if StageExecution should be executed immediately without starting its Trigger
    :return: None
    """
    arguments = {"immediately": immediately}
    response = ctx.obj.api_post(StageExecution.RE_EXECUTE, execution_id, json=arguments)
    helpers.print_message(response, ctx.obj.debug)

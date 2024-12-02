import click

from cryton.cli.utility import helpers
from cryton.cli.utility.decorators import *
from cryton.cli.config import Step, StepExecution


@click.group("steps")
@click.pass_context
def step(_) -> None:
    """
    Manage Steps from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@step.command("list")
@click.pass_context
@common_list_decorators
@click.option("-p", "--parent", type=click.INT, help="Filter Steps using Stage ID.")
def step_list(
    ctx: helpers.Context,
    less: bool,
    offset: int,
    limit: int,
    localize: bool,
    parameter_filters: tuple[tuple[str, str | int]],
    parent: int,
) -> None:
    """
    List existing Steps in Cryton.

    \f
    :param ctx: Click ctx object
    :param less: Show less like output
    :param offset: Initial index from which to return the results
    :param limit: Number of results per page
    :param localize: If datetime variables should be converted to local timezone
    :param parameter_filters: Filter results using returned parameters
    :param parent: Stage ID used to filter returned Steps
    :return: None
    """
    additional_parameters = {each[0]: each[1] for each in parameter_filters}
    if parent is not None:
        additional_parameters["stage_id"] = parent
    include = ["id", "name", "metadata", "module", "arguments", "is_init"]
    ctx.obj.get_items(Step.LIST, offset, limit, additional_parameters, include, less, localize)


@step.command("create")
@click.pass_context
@click.argument("stage_id", type=click.INT, required=True)
@click.argument("file", type=click.Path(exists=True), required=True)
@click.option(
    "-i",
    "--inventory-file",
    "inventory_files",
    type=click.Path(exists=True),
    multiple=True,
    help="Inventory file used to fill the template. Can be used multiple times.",
)
def step_create(ctx: helpers.Context, stage_id: int, file: str, inventory_files: list) -> None:
    """
    Create Step from FILE and add it to Stage with STAGE_ID.

    STAGE_ID is an ID of the Stage you want to add the Stage to.
    FILE is a path to the file containing the Step template.

    \f
    :param ctx: Click ctx object
    :param stage_id: ID of the Stage to use
    :param file: File used as the Step template
    :param inventory_files: Inventory file(s) used to fill the template
    :return: None
    """
    data = {"stage_id": stage_id}
    files = helpers.load_files(inventory_files)
    with open(file, "rb") as f:
        files["file"] = f.read()
    response = ctx.obj.api_post(Step.CREATE, data=data, files=files)
    helpers.print_message(response, ctx.obj.debug)


@step.command("show")
@click.pass_context
@click.argument("step_id", type=click.INT, required=True)
@d_less
@d_localize
def step_read(ctx: helpers.Context, step_id: int, less: bool, localize: bool) -> None:
    """
    Show Step with STEP_ID saved in Cryton.

    STEP_ID is ID of the Step you want to see.

    \f
    :param ctx: Click ctx object
    :param step_id: ID of the desired Step
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(Step.READ, step_id)
    include = ["id", "name", "metadata", "module", "arguments", "is_init"]
    helpers.print_items(response, include, less, localize, ctx.obj.debug)


@step.command("delete")
@click.pass_context
@click.argument("step_id", type=click.INT, required=True)
def step_delete(ctx: helpers.Context, step_id: int) -> None:
    """
    Delete Step with STEP_ID saved in Cryton.

    STEP_ID is ID of the Step you want to delete.

    \f
    :param ctx: Click ctx object
    :param step_id: ID of the desired Step
    :return: None
    """
    ctx.obj.delete_item(Step.DELETE, step_id)


@step.command("validate")
@click.pass_context
@click.argument("file", type=click.Path(exists=True), required=True)
@click.argument("stage_id", type=click.INT, required=True)
@click.option(
    "-i",
    "--inventory-file",
    "inventory_files",
    type=click.Path(exists=True),
    multiple=True,
    help="Inventory file used to fill the template. Can be used multiple times.",
)
def step_validate(ctx: helpers.Context, file: str, stage_id: int, inventory_files: list) -> None:
    """
    Validate FILE containing step against a stage with STAGE_ID.

    FILE is path/to/your/file that you want to validate.
    STAGE_ID is an ID of the stage you want to validate the step against.

    \f
    :param ctx: Click ctx object
    :param stage_id: ID of the Stage to use
    :param file: File used as the Step template
    :param inventory_files: Inventory file(s) used to fill the template
    :return: None
    """
    data = {"stage_id": stage_id}
    files = helpers.load_files(inventory_files)
    with open(file, "rb") as f:
        files["file"] = f.read()
    response = ctx.obj.api_post(Step.VALIDATE, data=data, files=files)
    helpers.print_message(response, ctx.obj.debug)


@step.command("execute")
@click.pass_context
@click.argument("step_id", type=click.INT, required=True)
@click.argument("stage_execution_id", type=click.INT, required=True)
def step_execute(ctx: helpers.Context, step_id: int, stage_execution_id: int) -> None:
    """
    Execute Step with STEP_ID under Stage execution with STAGE_EXECUTION_ID.

    STEP_ID is ID of the Step you want to execute.
    STAGE_EXECUTION_ID is an ID of the Stage execution you want to set as a parent of the Step execution.

    \f
    :param ctx: Click ctx object
    :param step_id: ID of the Step that will be used to create execution
    :param stage_execution_id: ID of the Stage execution that will be set as a parent of the Step execution
    :return: None
    """
    arguments = {"stage_execution_id": stage_execution_id}
    response = ctx.obj.api_post(Step.EXECUTE, step_id, json=arguments)
    helpers.print_message(response, ctx.obj.debug)


@click.group("step-executions")
@click.pass_context
def step_execution(_) -> None:
    """
    Manage Step's executions from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@step_execution.command("list")
@click.pass_context
@common_list_decorators
@click.option("-p", "--parent", type=click.INT, help="Filter Step executions using Stage execution ID.")
def step_execution_list(
    ctx: helpers.Context,
    less: bool,
    offset: int,
    limit: int,
    localize: bool,
    parameter_filters: tuple[tuple[str, str | int]],
    parent: int,
) -> None:
    """
    List existing Step's executions in Cryton.

    \f
    :param ctx: Click ctx object
    :param less: Show less like output
    :param offset: Initial index from which to return the results
    :param limit: Number of results per page
    :param localize: If datetime variables should be converted to local timezone
    :param parent: Stage execution ID used to filter returned Step executions
    :param parameter_filters: Filter results using returned parameters (for example `id`, `name`, etc.)
    :return: None
    """
    additional_parameters = {each[0]: each[1] for each in parameter_filters}
    if parent is not None:
        additional_parameters["stage_execution_id"] = parent
    include = [
        "id",
        "start_time",
        "pause_time",
        "finish_time",
        "state",
        "result",
        "evidence_file",
        "parent_id",
        "valid",
    ]
    ctx.obj.get_items(StepExecution.LIST, offset, limit, additional_parameters, include, less, localize)


@step_execution.command("delete")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
def step_execution_delete(ctx: helpers.Context, execution_id: int) -> None:
    """
    Delete Step's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Step's execution you want to delete.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Step's execution
    :return: None
    """
    ctx.obj.delete_item(StepExecution.DELETE, execution_id)


@step_execution.command("show")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
@d_less
@d_localize
def step_execution_read(ctx: helpers.Context, execution_id: int, less: bool, localize: bool) -> None:
    """
    Show Step's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Step's execution you want to see.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Step's execution
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(StepExecution.READ, execution_id)
    include = [
        "id",
        "start_time",
        "pause_time",
        "finish_time",
        "state",
        "result",
        "evidence_file",
        "parent_id",
        "valid",
        "mod_out",
        "mod_err",
        "std_out",
        "std_err",
    ]
    helpers.print_items(response, include, less, localize, ctx.obj.debug)


@step_execution.command("report")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
@d_save_report
@d_less
@d_localize
def step_execution_report(ctx: helpers.Context, execution_id: int, file: str, less: bool, localize: bool) -> None:
    """
    Create report for Step's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Step's execution you want to create report for.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Step's execution
    :param file: File to save the report to (default is /tmp)
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(StepExecution.REPORT, execution_id)
    helpers.save_yaml(response, file, f"step-execution-{execution_id}.yml", less, less, localize, ctx.obj.debug)


@step_execution.command("stop")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
def step_execution_stop(ctx: helpers.Context, execution_id: int) -> None:
    """
    Stop Step's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Step's execution you want to stop.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Step's execution
    :return: None
    """
    response = ctx.obj.api_post(StepExecution.STOP, execution_id)
    helpers.print_message(response, ctx.obj.debug)


@step_execution.command("re-execute")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
def step_execution_re_execute(ctx: helpers.Context, execution_id: int) -> None:
    """
    Re-execute Step's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Step's execution you want to re-execute.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Step's execution
    :return: None
    """
    response = ctx.obj.api_post(StepExecution.RE_EXECUTE, execution_id)
    helpers.print_message(response, ctx.obj.debug)

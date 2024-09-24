import click
from typing import Union

from cryton.cli.utility import helpers
from cryton.cli.utility.decorators import *
from cryton.cli.config import Plan, PlanExecution


@click.group("plans")
@click.pass_context
def plan(_) -> None:
    """
    Manage Plans from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@plan.command("list")
@click.pass_context
@common_list_decorators
def plan_list(
    ctx: helpers.Context,
    less: bool,
    offset: int,
    limit: int,
    localize: bool,
    parameter_filters: tuple[tuple[str, Union[str, int]]],
) -> None:
    """
    List existing Plans.

    \f
    :param ctx: Click ctx object
    :param less: Show less like output
    :param offset: Initial index from which to return the results
    :param limit: Number of results per page
    :param localize: If datetime variables should be converted to local timezone
    :param parameter_filters: Filter results using returned parameters
    :return: None
    """
    additional_parameters = {each[0]: each[1] for each in parameter_filters}
    include = ["id", "name", "metadata", "evidence_dir"]
    ctx.obj.get_items(Plan.LIST, offset, limit, additional_parameters, include, less, localize)


@plan.command("create")
@click.pass_context
@click.argument("template_id", type=click.INT, required=True)
@click.option(
    "-i",
    "--inventory-file",
    "inventory_files",
    type=click.Path(exists=True),
    multiple=True,
    help="Inventory file used to fill the template. Can be used multiple times.",
)
def plan_create(ctx: helpers.Context, template_id: int, inventory_files: list[str]) -> None:
    """
    Fill template PLAN_TEMPLATE_ID with inventory file(s) and save it to Cryton.

    PLAN_TEMPLATE_ID is ID of the template you want to fill.

    \f
    :param ctx: Click ctx object
    :param template_id: ID of the Plan's template to use
    :param inventory_files: Inventory file(s) used to fill the template
    :return: None
    """
    files = helpers.load_files(inventory_files)
    data = {"template_id": template_id}
    response = ctx.obj.api_post(Plan.CREATE, data=data, files=files)
    helpers.print_message(response, ctx.obj.debug)


@plan.command("show")
@click.pass_context
@click.argument("plan_id", type=click.INT, required=True)
@d_less
@d_localize
def plan_read(ctx: helpers.Context, plan_id: int, less: bool, localize: bool) -> None:
    """
    Show Plan with PLAN_ID saved in Cryton.

    PLAN_ID is ID of the Plan you want to see.

    \f
    :param ctx: Click ctx object
    :param plan_id: ID of the desired Plan
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(Plan.READ, plan_id)
    include = ["id", "name", "metadata", "evidence_dir"]
    helpers.print_items(response, include, less, localize, ctx.obj.debug)


@plan.command("delete")
@click.pass_context
@click.argument("plan_id", type=click.INT, required=True)
def plan_delete(ctx: helpers.Context, plan_id: int) -> None:
    """
    Delete Plan with PLAN_ID saved in Cryton.

    PLAN_ID is ID of the Plan you want to delete.

    \f
    :param ctx: Click ctx object
    :param plan_id: ID of the desired Plan
    :return: None
    """
    ctx.obj.delete_item(Plan.DELETE, plan_id)


@plan.command("validate")
@click.pass_context
@click.argument("file", type=click.Path(exists=True), required=True)
@click.option(
    "-i",
    "--inventory-file",
    "inventory_files",
    type=click.Path(exists=True),
    multiple=True,
    help="Inventory file used to fill the template. Can be used multiple times.",
)
def plan_validate(ctx: helpers.Context, file: str, inventory_files: list[str]) -> None:
    """
    Validate (syntax check) your FILE with Plan.

    FILE is path/to/your/file that you want to validate.

    \f
    :param ctx: Click ctx object
    :param file: File containing your Plan in yaml
    :param inventory_files: Inventory file(s) used to fill the template
    :return: None
    """
    files = helpers.load_files(inventory_files)
    with open(file, "rb") as f:
        files["file"] = f.read()

    response = ctx.obj.api_post(Plan.VALIDATE, files=files)
    helpers.print_message(response, ctx.obj.debug)


@plan.command("execute")
@click.pass_context
@click.argument("plan_id", type=click.INT, required=True)
@click.argument("worker_id", type=click.INT, required=True)
@click.argument("run_id", type=click.INT, required=True)
def plan_execute(ctx: helpers.Context, plan_id: int, worker_id: int, run_id: int) -> None:
    """
    Execute Plan saved in Cryton with PLAN_ID on Worker with WORKER_ID and attach it to Run with RUN_ID.

    PLAN_ID is ID of the Plan you want to execute.

    WORKER_ID is ID of the Plan you want to execute.

    RUN_ID is ID of the Run you want to attach this execution to.

    \f
    :param ctx: Click ctx object
    :param plan_id: ID of the desired Plan
    :param worker_id: ID of the desired Worker
    :param run_id: ID of the desired Run
    :return: None
    """
    arguments = {"run_id": run_id, "worker_id": worker_id}
    response = ctx.obj.api_post(Plan.EXECUTE, plan_id, json=arguments)
    helpers.print_message(response, ctx.obj.debug)


@plan.command("get-plan")
@click.pass_context
@click.argument("plan_id", type=click.INT, required=True)
@d_save_report
@d_less
@d_localize
def plan_get_plan(ctx: helpers.Context, plan_id: int, file: str, less: bool, localize: bool) -> None:
    """
    Get Plan with PLAN_ID saved in Cryton.

    PLAN_ID is ID of the Plan you want to get.

    \f
    :param ctx: Click ctx object
    :param plan_id: ID of the desired Plan
    :param file: File to save the plan to (default is /tmp)
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(Plan.GET_PLAN, plan_id)
    helpers.save_yaml(response, file, f"plan-{plan_id}.yml", less, less, localize, ctx.obj.debug)


@click.group("plan-executions")
@click.pass_context
def plan_execution(_) -> None:
    """
    Manage Plan's executions from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@plan_execution.command("list")
@click.pass_context
@common_list_decorators
@click.option("-p", "--parent", type=click.INT, help="Filter Plan executions using Run ID.")
def plan_execution_list(
    ctx: helpers.Context,
    less: bool,
    offset: int,
    limit: int,
    localize: bool,
    parameter_filters: tuple[tuple[str, Union[str, int]]],
    parent: int,
) -> None:
    """
    List existing Plan's executions in Cryton.

    \f
    :param ctx: Click ctx object
    :param less: Show less like output
    :param offset: Initial index from which to return the results
    :param limit: Number of results per page
    :param localize: If datetime variables should be converted to local timezone
    :param parameter_filters: Filter results using returned parameters
    :param parent: Run ID used to filter returned Plan executions
    :return: None
    """
    additional_parameters = {each[0]: each[1] for each in parameter_filters}
    if parent is not None:
        additional_parameters["run_id"] = parent
    include = ["id", "schedule_time", "start_time", "pause_time", "finish_time", "state", "evidence_dir", "worker"]
    ctx.obj.get_items(PlanExecution.LIST, offset, limit, additional_parameters, include, less, localize)


@plan_execution.command("delete")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
def plan_execution_delete(ctx: helpers.Context, execution_id: int) -> None:
    """
    Delete Plan's execution with EXECUTION_ID.

    EXECUTION_ID is ID of the Plan's execution you want to delete.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Plan's execution
    :return: None
    """
    ctx.obj.delete_item(PlanExecution.DELETE, execution_id)


@plan_execution.command("show")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
@d_less
@d_localize
def plan_execution_read(ctx: helpers.Context, execution_id: int, less: bool, localize: bool) -> None:
    """
    Show Plan's execution with EXECUTION_ID.

    EXECUTION_ID is ID of the Plan's execution you want to see.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Plan's execution
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(PlanExecution.READ, execution_id)
    include = ["id", "schedule_time", "start_time", "pause_time", "finish_time", "state", "evidence_dir", "worker"]
    helpers.print_items(response, include, less, localize, ctx.obj.debug)


@plan_execution.command("pause")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
def plan_execution_pause(ctx: helpers.Context, execution_id: int) -> None:
    """
    Pause Plan's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Plan's execution you want to pause.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Plan's execution
    :return: None
    """
    response = ctx.obj.api_post(PlanExecution.PAUSE, execution_id)
    helpers.print_message(response, ctx.obj.debug)


@plan_execution.command("report")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
@d_save_report
@d_less
@d_localize
def plan_execution_report(ctx: helpers.Context, execution_id: int, file: str, less: bool, localize: bool) -> None:
    """
    Create report for Plan's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Plan's execution you want to create report for.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Plan's execution
    :param file: File to save the report to (default is /tmp)
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(PlanExecution.REPORT, execution_id)
    helpers.save_yaml(response, file, f"plan-execution-{execution_id}.yml", less, less, localize, ctx.obj.debug)


@plan_execution.command("resume")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
def plan_execution_unpause(ctx: helpers.Context, execution_id: int) -> None:
    """
    Resume Plan's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Plan's execution you want to resume.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Plan's execution
    :return: None
    """
    response = ctx.obj.api_post(PlanExecution.UNPAUSE, execution_id)
    helpers.print_message(response, ctx.obj.debug)


@plan_execution.command("validate-modules")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
def plan_execution_validate_modules(ctx: helpers.Context, execution_id: int) -> None:
    """
    Validate modules for Plan's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Plan's execution you want to validate modules for.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Plan's execution
    :return: None
    """
    response = ctx.obj.api_post(PlanExecution.VALIDATE_MODULES, execution_id)
    helpers.print_message(response, ctx.obj.debug)


@plan_execution.command("kill")
@click.pass_context
@click.argument("execution_id", type=click.INT, required=True)
def plan_execution_kill(ctx: helpers.Context, execution_id: int) -> None:
    """
    Kill Plan's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Plan's execution you want to kill.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Plan's execution
    :return: None
    """
    response = ctx.obj.api_post(PlanExecution.KILL, execution_id)
    helpers.print_message(response, ctx.obj.debug)

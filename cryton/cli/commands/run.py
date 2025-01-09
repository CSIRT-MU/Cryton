import click

from cryton.cli.utility import helpers
from cryton.cli.utility.decorators import *
from cryton.cli.config import Run, SETTINGS


@click.group("runs", helpers.AliasedGroup)
@click.pass_context
def run(_) -> None:
    """
    Manage Runs from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@run.command("list")
@click.pass_context
@common_list_decorators
def run_list(
    ctx: helpers.Context,
    less: bool,
    offset: int,
    limit: int,
    localize: bool,
    parameter_filters: tuple[tuple[str, str | int]],
) -> None:
    """
    List existing Runs in Cryton.

    \f
    :param ctx: Click ctx object
    :param less: Show less like output
    :param offset: Initial index from which to return the results
    :param limit: Number of results per page
    :param localize: If datetime variables should be converted to local timezone
    :param parameter_filters: Filter results using returned parameters (for example `id`, `name`, etc.)
    :return: None
    """
    additional_parameters = {each[0]: each[1] for each in parameter_filters}
    include = ["id", "schedule_time", "start_time", "pause_time", "finish_time", "state", "plan"]
    ctx.obj.get_items(Run.LIST, offset, limit, additional_parameters, include, less, localize)


@run.command("create")
@click.pass_context
@click.argument("plan_id", type=click.INT, required=True)
@click.argument("worker_ids", type=click.INT, nargs=-1, required=True)
def run_create(ctx: helpers.Context, plan_id: int, worker_ids: list) -> None:
    """
    Create new Run with PLAN_ID and WORKER_IDS.

    PLAN_ID is ID of the Plan you want to create Run for. (for example 1)

    WORKER_IDS is list of IDs you want to use for Run. (1 2 3)

    \f
    :param ctx: Click ctx object
    :param plan_id: ID of the Plan that will be used in Run
    :param worker_ids: List of IDs you want to use for Run
    :return: None
    """
    arguments = {"plan_id": plan_id, "worker_ids": worker_ids}
    response = ctx.obj.api_post(Run.CREATE, json=arguments)
    helpers.print_message(response, ctx.obj.debug)


@run.command("show")
@click.pass_context
@click.argument("run_id", type=click.INT, required=True)
@d_less
@d_localize
def run_read(ctx: helpers.Context, run_id: int, less: bool, localize: bool) -> None:
    """
    Show Run with RUN_ID saved in Cryton.

    RUN_ID is ID of the Run you want to see.

    \f
    :param ctx: Click ctx object
    :param run_id: ID of the desired Run
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(Run.READ, run_id)
    # TODO: move include into a global variable on top of the file
    include = ["id", "schedule_time", "start_time", "pause_time", "finish_time", "state", "plan"]
    helpers.print_items(response, include, less, localize, ctx.obj.debug)


@run.command("delete")
@click.pass_context
@click.argument("run_id", type=click.INT, required=True)
def run_delete(ctx: helpers.Context, run_id: int) -> None:
    """
    Delete Run with RUN_ID saved in Cryton.

    RUN_ID is ID of the Run you want to delete.

    \f
    :param ctx: Click ctx object
    :param run_id: ID of the desired Run
    :return: None
    """
    ctx.obj.delete_item(Run.DELETE, run_id)


@run.command("execute")
@click.pass_context
@click.argument("run_id", type=click.INT, required=True)
@click.option("-S", "--skip-checks", is_flag=True, help="Skip health-checks and modules validation.")
def run_execute(ctx: helpers.Context, run_id: int, skip_checks: bool) -> None:
    """
    Execute Run saved in Cryton with RUN_ID.

    RUN_ID is ID of the Run you want to execute.

    \f
    :param skip_checks: Skip health-checks and modules validation
    :param ctx: Click ctx object
    :param run_id: ID of the desired Run
    :return: None
    """
    if not skip_checks:
        click.echo("Checking if Workers are available..")
        workers_health_check = ctx.invoke(run_health_check_workers, run_id=run_id)
        click.echo("Checking if modules are available and the Plan is correct..")
        modules_validation = ctx.invoke(run_validate_modules, run_id=run_id)
        if not (workers_health_check and modules_validation):
            click.secho("Unable to execute the Run. To skip checks use the option `--skip-checks`.", fg="red")
            return

    response = ctx.obj.api_post(Run.EXECUTE, run_id)
    helpers.print_message(response, ctx.obj.debug)


@run.command("pause")
@click.pass_context
@click.argument("run_id", type=click.INT, required=True)
def run_pause(ctx: helpers.Context, run_id: int) -> None:
    """
    Pause Run saved in Cryton with RUN_ID.

    RUN_ID is ID of the Run you want to pause.

    \f
    :param ctx: Click ctx object
    :param run_id: ID of the desired Run
    :return: None
    """
    response = ctx.obj.api_post(Run.PAUSE, run_id)
    helpers.print_message(response, ctx.obj.debug)


@run.command("report")
@click.pass_context
@click.argument("run_id", type=click.INT, required=True)
@d_save_report
@d_less
@d_localize
def run_report(ctx: helpers.Context, run_id: int, file: str, less: bool, localize: bool) -> None:
    """
    Create report for Run with RUN_ID saved in Cryton.

    RUN_ID is ID of the Run you want to create report for.

    \f
    :param ctx: Click ctx object
    :param run_id: ID of the desired Run
    :param file: File to save the report to (default is /tmp)
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(Run.REPORT, run_id)
    helpers.save_yaml(response, file, f"run-{run_id}.yml", less, less, localize, ctx.obj.debug)


@run.command("reschedule")
@click.pass_context
@click.argument("run_id", type=click.INT, required=True)
@click.argument("to_date", type=click.STRING, required=True)
@click.argument("to_time", type=click.STRING, required=True)
@click.option("--utc-timezone", is_flag=True, help="Input time in UTC timezone.")
def run_reschedule(ctx: helpers.Context, run_id: int, to_date: str, to_time: str, utc_timezone: bool) -> None:
    """
    Reschedule Run saved in Cryton with RUN_ID to specified DATE and TIME.

    RUN_ID is ID of the Run you want to reschedule.

    DATE in format year-month-day (Y-m-d).

    TIME in format hours:minutes:seconds (H:M:S).

    \f
    :param ctx: Click ctx object
    :param run_id: ID of the desired Run
    :param to_date: to what date you want to reschedule Run
    :param to_time: to what time you want to reschedule Run
    :param utc_timezone: Use UTC timezone instead of local timezone
    :return: None
    """
    arguments = {"start_time": f"{to_date}T{to_time}Z", "time_zone": "UTC" if utc_timezone else SETTINGS.timezone}
    response = ctx.obj.api_post(Run.RESCHEDULE, run_id, json=arguments)
    helpers.print_message(response, ctx.obj.debug)


@run.command("schedule")
@click.pass_context
@click.argument("run_id", type=click.INT, required=True)
@click.argument("to_date", type=click.STRING, required=True)
@click.argument("to_time", type=click.STRING, required=True)
@click.option("--utc-timezone", is_flag=True, help="Input time in UTC timezone.")
def run_schedule(ctx: helpers.Context, run_id: int, to_date: str, to_time: str, utc_timezone: bool) -> None:
    """
    Schedule Run saved in Cryton with RUN_ID to specified DATE and TIME.

    RUN_ID is ID of the Run you want to schedule.

    DATE in format year-month-day (Y-m-d).

    TIME in format hours:minutes:seconds (H:M:S).

    \f
    :param ctx: Click ctx object
    :param run_id: ID of the desired Run
    :param to_date: to what date you want to reschedule Run
    :param to_time: to what time you want to reschedule Run
    :param utc_timezone: Use UTC timezone instead of local timezone
    :return: None
    """
    arguments = {"start_time": f"{to_date}T{to_time}Z", "time_zone": "UTC" if utc_timezone else SETTINGS.timezone}
    response = ctx.obj.api_post(Run.SCHEDULE, run_id, json=arguments)
    helpers.print_message(response, ctx.obj.debug)


@run.command("resume")
@click.pass_context
@click.argument("run_id", type=click.INT, required=True)
def run_resume(ctx: helpers.Context, run_id: int) -> None:
    """
    Resume Run saved in Cryton with RUN_ID.

    RUN_ID is ID of the Run you want to resume.

    \f
    :param ctx: Click ctx object
    :param run_id: ID of the desired Run
    :return: None
    """
    response = ctx.obj.api_post(Run.RESUME, run_id)
    helpers.print_message(response, ctx.obj.debug)


@run.command("unschedule")
@click.pass_context
@click.argument("run_id", type=click.INT, required=True)
def run_unschedule(ctx: helpers.Context, run_id: int) -> None:
    """
    Unschedule Run saved in Cryton with RUN_ID.

    RUN_ID is ID of the Run you want to unschedule.

    \f
    :param ctx: Click ctx object
    :param run_id: ID of the desired Run
    :return: None
    """
    response = ctx.obj.api_post(Run.UNSCHEDULE, run_id)
    helpers.print_message(response, ctx.obj.debug)


@run.command("stop")
@click.pass_context
@click.argument("run_id", type=click.INT, required=True)
def run_stop(ctx: helpers.Context, run_id: int) -> None:
    """
    Stop Run saved in Cryton with RUN_ID.

    RUN_ID is ID of the Run you want to stop.

    \f
    :param ctx: Click ctx object
    :param run_id: ID of the desired Run
    :return: None
    """
    response = ctx.obj.api_post(Run.STOP, run_id)
    helpers.print_message(response, ctx.obj.debug)


@run.command("health-check-workers")
@click.pass_context
@click.argument("run_id", type=click.INT, required=True)
def run_health_check_workers(ctx: helpers.Context, run_id: int) -> bool:
    """
    Check Workers for Run with RUN_ID saved in Cryton.

    RUN_ID is ID of the Run you want to check Workers for.

    \f
    :param ctx: Click ctx object
    :param run_id: ID of the desired Run
    :return: True when the results are OK
    """
    response = ctx.obj.api_post(Run.HEALTH_CHECK_WORKERS, run_id)
    return helpers.print_message(response, ctx.obj.debug)


@run.command("validate-modules")
@click.pass_context
@click.argument("run_id", type=click.INT, required=True)
def run_validate_modules(ctx: helpers.Context, run_id: int) -> bool:
    """
    Validate modules for Run with RUN_ID saved in Cryton.

    RUN_ID is ID of the Run you want to validate modules for.

    \f
    :param ctx: Click ctx object
    :param run_id: ID of the desired Run
    :return: True when the results are OK
    """
    response = ctx.obj.api_post(Run.VALIDATE_MODULES, run_id)
    return helpers.print_message(response, ctx.obj.debug)


@run.command("get-plan")
@click.pass_context
@click.argument("run_id", type=click.INT, required=True)
@click.option(
    "-f", "--file", type=click.Path(exists=True), default="/tmp", help="File to save the plan to (default is /tmp)."
)
@d_less
@d_localize
def run_get_plan(ctx: helpers.Context, run_id: int, file: str, less: bool, localize: bool) -> None:
    """
    Get plan from Run with RUN_ID saved in Cryton.

    RUN_ID is ID of the Run you want to get plan from.

    \f
    :param ctx: Click ctx object
    :param run_id: ID of the desired Run
    :param file: File to save the plan to (default is /tmp)
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(Run.GET_PLAN, run_id)
    helpers.save_yaml(response, file, f"plan-used-in-run-{run_id}.yml", less, less, localize, ctx.obj.debug)

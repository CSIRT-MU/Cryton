import click
from typing import List, Optional

from cryton_cli.lib.util import api, util


# Plan
@click.group('plans')
@click.pass_context
def plan(_) -> None:
    """
    Manage Plans from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@plan.command('list')
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('-o', '--offset', type=click.INT, default=0, help='The initial index from which to return the results.')
@click.option('-l', '--limit', type=click.INT, default=20, help='Number of results to return per page.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.option('-f', '--filter', 'parameter_filters', type=click.STRING, multiple=True,
              help='Filter results using returned parameters (for example `id=1`, `name=test`, etc.).')
@click.pass_context
def plan_list(ctx: click.Context, less: bool, offset: int, limit: int, localize: bool, 
              parameter_filters: Optional[List[str]]) -> None:
    """
    List existing Plans in Cryton.

    \f
    :param ctx: Click ctx object
    :param less: Show less like output
    :param offset: Initial index from which to return the results
    :param limit: Number of results per page
    :param localize: If datetime variables should be converted to local timezone
    :param parameter_filters: Filter results using returned parameters (for example `id`, `name`, etc.)
    :return: None
    """
    results_filter = "&".join(parameter_filters)
    appendix = f'?limit={limit}&offset={offset}&{results_filter}'
    response = api.get_request(ctx.obj.api_url, api.PLAN_LIST + appendix)

    to_print = ['id', 'name', 'owner', 'evidence_dir']
    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@plan.command('create')
@click.argument('template_id', type=click.INT, required=True)
@click.option('-i', '--inventory-file', 'inventory_files', type=click.Path(exists=True), multiple=True,
              help="Inventory file used to fill the template. Can be used multiple times.")
@click.pass_context
def plan_create(ctx: click.Context, template_id: int, inventory_files: list) -> None:
    """
    Fill template PLAN_TEMPLATE_ID with inventory file(s) and save it to Cryton.

    PLAN_TEMPLATE_ID is ID of the template you want to fill.

    \f
    :param ctx: Click ctx object
    :param template_id: ID of the Plan's template to use
    :param inventory_files: Inventory file(s) used to fill the template
    :return: None
    """
    files = util.load_files(inventory_files)
    data = {'template_id': template_id}

    response = api.post_request(ctx.obj.api_url, api.PLAN_CREATE, files=files, data=data)
    util.echo_msg(response, 'Plan Instance successfully created!', ctx.obj.debug)


@plan.command('show')
@click.argument('plan_id', type=click.INT, required=True)
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.pass_context
def plan_read(ctx: click.Context, plan_id: int, less: bool, localize: bool) -> None:
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
    response = api.get_request(ctx.obj.api_url, api.PLAN_READ, plan_id)

    to_print = ['id', 'name', 'owner', 'evidence_dir']
    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@plan.command('delete')
@click.argument('plan_id', type=click.INT, required=True)
@click.pass_context
def plan_delete(ctx: click.Context, plan_id: int) -> None:
    """
    Delete Plan with PLAN_ID saved in Cryton.

    PLAN_ID is ID of the Plan you want to delete.

    \f
    :param ctx: Click ctx object
    :param plan_id: ID of the desired Plan
    :return: None
    """
    response = api.delete_request(ctx.obj.api_url, api.PLAN_DELETE, plan_id)

    util.echo_msg(response, 'Plan successfully deleted!', ctx.obj.debug)


@plan.command('validate')
@click.argument('file', type=click.Path(exists=True), required=True)
@click.option('-i', '--inventory-file', 'inventory_files', type=click.Path(exists=True), multiple=True,
              help="Inventory file used to fill the template. Can be used multiple times.")
@click.pass_context
def plan_validate(ctx: click.Context, file: str, inventory_files: list) -> None:
    """
    Validate (syntax check) your FILE with Plan.

    FILE is path/to/your/file that you want to validate.

    \f
    :param ctx: Click ctx object
    :param file: File containing your Plan in yaml
    :param inventory_files: Inventory file(s) used to fill the template
    :return: None
    """
    with open(file, "rb") as f:
        files = {'file': f.read()}

    files.update(util.load_files(inventory_files))

    response = api.post_request(ctx.obj.api_url, api.PLAN_VALIDATE, files=files)

    util.echo_msg(response, 'Plan successfully validated!', ctx.obj.debug)


@plan.command('execute')
@click.argument('plan_id', type=click.INT, required=True)
@click.argument('worker_id', type=click.INT, required=True)
@click.argument('run_id', type=click.INT, required=True)
@click.pass_context
def plan_execute(ctx: click.Context, plan_id: int, worker_id: int, run_id: int) -> None:
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
    arguments = {'run_id': run_id, 'worker_id': worker_id}
    response = api.post_request(ctx.obj.api_url, api.PLAN_EXECUTE, plan_id, arguments)

    util.echo_msg(response, 'Plan successfully executed!', ctx.obj.debug)


@plan.command('get-plan')
@click.argument('plan_id', type=click.INT, required=True)
@click.option('-f', '--file', type=click.Path(exists=True), default='/tmp',
              help='File to save the plan to (default is /tmp).')
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.pass_context
def plan_get_plan(ctx: click.Context, plan_id: int, file: str, less: bool, localize: bool) -> None:
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
    response = api.get_request(ctx.obj.api_url, api.PLAN_GET_PLAN, plan_id)

    util.get_yaml(response, file, f'plan-yaml_{plan_id}', less, less, localize, ctx.obj.debug)


# PlanExecution
@click.group('plan-executions')
@click.pass_context
def plan_execution(_) -> None:
    """
    Manage Plan's executions from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@plan_execution.command('list')
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('-o', '--offset', type=click.INT, default=0, help='The initial index from which to return the results.')
@click.option('-l', '--limit', type=click.INT, default=20, help='Number of results to return per page.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.option('-p', '--parent', type=click.INT, help='Filter Plan executions using Run ID.')
@click.option('-f', '--filter', 'parameter_filters', type=click.STRING, multiple=True,
              help='Filter results using returned parameters (for example `id=1`, `name=test`, etc.).')
@click.pass_context
def plan_execution_list(ctx: click.Context, less: bool, offset: int, limit: int, localize: bool, parent: int, 
                        parameter_filters: Optional[List[str]]) -> None:
    """
    List existing Plan's executions in Cryton.

    \f
    :param ctx: Click ctx object
    :param less: Show less like output
    :param offset: Initial index from which to return the results
    :param limit: Number of results per page
    :param localize: If datetime variables should be converted to local timezone
    :param parent: Run ID used to filter returned Plan executions
    :param parameter_filters: Filter results using returned parameters (for example `id`, `name`, etc.)
    :return: None
    """
    results_filter = "&".join(parameter_filters)
    appendix = f'?limit={limit}&offset={offset}&{results_filter}'
    custom_params = {}
    if parent is not None:
        custom_params.update({'run_id': parent})
    response = api.get_request(ctx.obj.api_url, api.PLAN_EXECUTION_LIST + appendix, custom_params=custom_params)

    to_print = ['id', 'schedule_time', 'start_time', 'pause_time', 'finish_time', 'state', 'evidence_dir', 'worker']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@plan_execution.command('delete')
@click.argument('execution_id', type=click.INT, required=True)
@click.pass_context
def plan_execution_delete(ctx: click.Context, execution_id: int) -> None:
    """
    Delete Plan's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Plan's execution you want to delete.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Plan's execution
    :return: None
    """
    response = api.delete_request(ctx.obj.api_url, api.PLAN_EXECUTION_DELETE, execution_id)

    util.echo_msg(response, 'Plan execution successfully deleted!', ctx.obj.debug)


@plan_execution.command('show')
@click.argument('execution_id', type=click.INT, required=True)
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.pass_context
def plan_execution_read(ctx: click.Context, execution_id: int, less: bool, localize: bool) -> None:
    """
    Show Plan's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Plan's execution you want to see.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Plan's execution
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = api.get_request(ctx.obj.api_url, api.PLAN_EXECUTION_READ, execution_id)

    to_print = ['id', 'schedule_time', 'start_time', 'pause_time', 'finish_time', 'state', 'evidence_dir', 'worker']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@plan_execution.command('pause')
@click.argument('execution_id', type=click.INT, required=True)
@click.pass_context
def plan_execution_pause(ctx: click.Context, execution_id: int) -> None:
    """
    Pause Plan's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Plan's execution you want to pause.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Plan's execution
    :return: None
    """
    response = api.post_request(ctx.obj.api_url, api.PLAN_EXECUTION_PAUSE, execution_id)

    util.echo_msg(response, 'Plan execution successfully paused!', ctx.obj.debug)


@plan_execution.command('report')
@click.argument('execution_id', type=click.INT, required=True)
@click.option('-f', '--file', type=click.Path(exists=True), default='/tmp',
              help='File to save the report to (default is /tmp).')
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.pass_context
def plan_execution_report(ctx: click.Context, execution_id: int, file: str, less: bool, localize: bool) -> None:
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
    response = api.get_request(ctx.obj.api_url, api.PLAN_EXECUTION_REPORT, execution_id)

    util.get_yaml(response, file, f'report-plan-execution_{execution_id}', less, less, localize, ctx.obj.debug)


@plan_execution.command('resume')
@click.argument('execution_id', type=click.INT, required=True)
@click.pass_context
def plan_execution_unpause(ctx: click.Context, execution_id: int) -> None:
    """
    Resume Plan's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Plan's execution you want to resume.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Plan's execution
    :return: None
    """
    response = api.post_request(ctx.obj.api_url, api.PLAN_EXECUTION_UNPAUSE, execution_id)

    util.echo_msg(response, 'Plan execution successfully resumed!', ctx.obj.debug)


@plan_execution.command('validate-modules')
@click.argument('execution_id', type=click.INT, required=True)
@click.pass_context
def plan_execution_validate_modules(ctx: click.Context, execution_id: int) -> None:
    """
    Validate modules for Plan's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Plan's execution you want to validate modules for.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Plan's execution
    :return: None
    """
    response = api.post_request(ctx.obj.api_url, api.PLAN_EXECUTION_VALIDATE_MODULES, execution_id)

    util.echo_msg(response, 'Modules were validated!', ctx.obj.debug)


@plan_execution.command('kill')
@click.argument('execution_id', type=click.INT, required=True)
@click.pass_context
def plan_execution_kill(ctx: click.Context, execution_id: int) -> None:
    """
    Kill Plan's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Plan's execution you want to kill.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Plan's execution
    :return: None
    """
    response = api.post_request(ctx.obj.api_url, api.PLAN_EXECUTION_KILL, execution_id)

    util.echo_msg(response, 'Plan execution successfully killed!', ctx.obj.debug)

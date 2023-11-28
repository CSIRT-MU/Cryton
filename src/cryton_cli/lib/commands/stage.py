import click
from typing import List, Optional

from cryton_cli.lib.util import api, util


# Stage
@click.group('stages')
@click.pass_context
def stage(_) -> None:
    """
    Manage Stages from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@stage.command('list')
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('-o', '--offset', type=click.INT, default=0, help='The initial index from which to return the results.')
@click.option('-l', '--limit', type=click.INT, default=20, help='Number of results to return per page.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.option('-p', '--parent', type=click.INT, help='Filter Stages using Plan ID.')
@click.option('-f', '--filter', 'parameter_filters', type=click.STRING, multiple=True,
              help='Filter results using returned parameters (for example `id=1`, `name=test`, etc.).')
@click.pass_context
def stage_list(ctx: click.Context, less: bool, offset: int, limit: int, localize: bool, parent: int, 
               parameter_filters: Optional[List[str]]) -> None:
    """
    List existing Stages in Cryton.

    \f
    :param ctx: Click ctx object
    :param less: Show less like output
    :param offset: Initial index from which to return the results
    :param limit: Number of results per page
    :param localize: If datetime variables should be converted to local timezone
    :param parent: Plan ID used to filter returned Stages
    :param parameter_filters: Filter results using returned parameters (for example `id`, `name`, etc.)
    :return: None
    """
    results_filter = "&".join(parameter_filters)
    appendix = f'?limit={limit}&offset={offset}&{results_filter}'
    custom_params = {}
    if parent is not None:
        custom_params.update({'plan_model_id': parent})
    response = api.get_request(ctx.obj.api_url, api.STAGE_LIST + appendix, custom_params=custom_params)

    to_print = ['id', 'name', 'trigger_type', 'trigger_args', 'executor']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@stage.command('create')
@click.argument('plan_id', type=click.INT, required=True)
@click.argument('file', type=click.Path(exists=True), required=True)
@click.option('-i', '--inventory-file', 'inventory_files', type=click.Path(exists=True), multiple=True,
              help="Inventory file used to fill the template. Can be used multiple times.")
@click.pass_context
def stage_create(ctx: click.Context, plan_id: int, file: str, inventory_files: list) -> None:
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
    with open(file, "rb") as f:
        files = {'file': f.read()}

    files.update(util.load_files(inventory_files))

    response = api.post_request(ctx.obj.api_url, api.STAGE_CREATE, files=files, data={'plan_id': plan_id})

    util.echo_msg(response, 'Stage successfully created!', ctx.obj.debug)


@stage.command('show')
@click.argument('stage_id', type=click.INT, required=True)
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.pass_context
def stage_read(ctx: click.Context, stage_id: int, less: bool, localize: bool) -> None:
    """
    Show Stage with STAGE_ID saved in Cryton.

    STAGE_ID is ID of the Stage you want to see.

    \f
    :param ctx: Click ctx object
    :param stage_id: ID of the desired Stage
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = api.get_request(ctx.obj.api_url, api.STAGE_READ, stage_id)

    to_print = ['id', 'name', 'trigger_type', 'trigger_args', 'executor']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@stage.command('delete')
@click.argument('stage_id', type=click.INT, required=True)
@click.pass_context
def stage_delete(ctx: click.Context, stage_id: int) -> None:
    """
    Delete Stage with STAGE_ID saved in Cryton.

    STAGE_ID is ID of the Stage you want to delete.

    \f
    :param ctx: Click ctx object
    :param stage_id: ID of the desired Stage
    :return: None
    """
    response = api.delete_request(ctx.obj.api_url, api.STAGE_DELETE, stage_id)

    util.echo_msg(response, 'Stage successfully deleted!', ctx.obj.debug)


@stage.command('validate')
@click.argument('file', type=click.Path(exists=True), required=True)
@click.option('-i', '--inventory-file', 'inventory_files', type=click.Path(exists=True), multiple=True,
              help="Inventory file used to fill the template. Can be used multiple times.")
@click.option('-D', '--dynamic', is_flag=True, help='If Stage will be used with a dynamic Plan.')
@click.pass_context
def stage_validate(ctx: click.Context, file: str, inventory_files: list, dynamic: bool) -> None:
    """
    Validate (syntax check) your FILE with Stage.

    FILE is path/to/your/file that you want to validate.

    \f
    :param ctx: Click ctx object
    :param file: File containing your Stage in yaml
    :param inventory_files: Inventory file(s) used to fill the template
    :param dynamic: If Stage will be used with a dynamic Plan
    :return: None
    """
    with open(file, "rb") as f:
        files = {'file': f.read()}

    files.update(util.load_files(inventory_files))
    data = {"dynamic": dynamic}

    response = api.post_request(ctx.obj.api_url, api.STAGE_VALIDATE, files=files, data=data)

    util.echo_msg(response, 'Stage successfully validated!', ctx.obj.debug)


@stage.command('start-trigger')
@click.argument('stage_id', type=click.INT, required=True)
@click.argument('plan_execution_id', type=click.INT, required=True)
@click.pass_context
def stage_start_trigger(ctx: click.Context, stage_id: int, plan_execution_id: int) -> None:
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
    arguments = {'plan_execution_id': plan_execution_id}
    response = api.post_request(ctx.obj.api_url, api.STAGE_START_TRIGGER, stage_id, custom_dict=arguments)

    util.echo_msg(response, 'Stage\'s trigger successfully started!', ctx.obj.debug)


# StageExecution
@click.group('stage-executions')
@click.pass_context
def stage_execution(_) -> None:
    """
    Manage Stage's executions from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@stage_execution.command('list')
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('-o', '--offset', type=click.INT, default=0, help='The initial index from which to return the results.')
@click.option('-l', '--limit', type=click.INT, default=20, help='Number of results to return per page.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.option('-p', '--parent', type=click.INT, help='Filter Stage executions using Plan execution ID.')
@click.option('-f', '--filter', 'parameter_filters', type=click.STRING, multiple=True,
              help='Filter results using returned parameters (for example `id=1`, `name=test`, etc.).')
@click.pass_context
def stage_execution_list(ctx: click.Context, less: bool, offset: int, limit: int, localize: bool, parent: int, 
                         parameter_filters: Optional[List[str]]) -> None:
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
    results_filter = "&".join(parameter_filters)
    appendix = f'?limit={limit}&offset={offset}&{results_filter}'
    custom_params = {}
    if parent is not None:
        custom_params.update({'plan_execution_id': parent})
    response = api.get_request(ctx.obj.api_url, api.STAGE_EXECUTION_LIST + appendix, custom_params=custom_params)

    to_print = ['id', 'schedule_time', 'start_time', 'pause_time', 'finish_time', 'state']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@stage_execution.command('delete')
@click.argument('execution_id', type=click.INT, required=True)
@click.pass_context
def stage_execution_delete(ctx: click.Context, execution_id: int) -> None:
    """
    Delete Stage's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Stage's execution you want to delete.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Stage's execution
    :return: None
    """
    response = api.delete_request(ctx.obj.api_url, api.STAGE_EXECUTION_DELETE, execution_id)

    util.echo_msg(response, 'Stage execution successfully deleted!', ctx.obj.debug)


@stage_execution.command('show')
@click.argument('execution_id', type=click.INT, required=True)
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.pass_context
def stage_execution_read(ctx: click.Context, execution_id: int, less: bool, localize: bool) -> None:
    """
    Show Stage's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Stage's execution you want to see.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Stage's execution
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = api.get_request(ctx.obj.api_url, api.STAGE_EXECUTION_READ, execution_id)

    to_print = ['id', 'schedule_time', 'start_time', 'pause_time', 'finish_time', 'state']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@stage_execution.command('report')
@click.argument('execution_id', type=click.INT, required=True)
@click.option('-f', '--file', type=click.Path(exists=True), default='/tmp',
              help='File to save the report to (default is /tmp).')
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.pass_context
def stage_execution_report(ctx: click.Context, execution_id: int, file: str, less: bool,
                           localize: bool) -> None:
    """
    Create report for Stage's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Stage's execution you want to create report for.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Stage's execution
    :param file: File to save the report to (default is /tmp)
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = api.get_request(ctx.obj.api_url, api.STAGE_EXECUTION_REPORT, execution_id)

    util.get_yaml(response, file, f'report-stage-execution_{execution_id}', less, less, localize, ctx.obj.debug)


@stage_execution.command('kill')
@click.argument('execution_id', type=click.INT, required=True)
@click.pass_context
def stage_execution_kill(ctx: click.Context, execution_id: int) -> None:
    """
    Kill Stage's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Stage's execution you want to kill.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Stage's execution
    :return: None
    """
    response = api.post_request(ctx.obj.api_url, api.STAGE_EXECUTION_KILL, execution_id)

    util.echo_msg(response, 'Stage execution successfully killed!', ctx.obj.debug)


@stage_execution.command('re-execute')
@click.argument('execution_id', type=click.INT, required=True)
@click.option('--immediately', is_flag=True, help='Re-execute StageExecution immediately without starting its Trigger.')
@click.pass_context
def stage_execution_re_execute(ctx: click.Context, execution_id: int, immediately: bool) -> None:
    """
    Re-execute Stage's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Stage's execution you want to kill.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Stage's execution
    :param immediately: True if StageExecution should be executed immediately without starting its Trigger
    :return: None
    """
    response = api.post_request(ctx.obj.api_url, api.STAGE_EXECUTION_RE_EXECUTE, execution_id,
                                {"immediately": immediately})

    util.echo_msg(response, 'Stage execution successfully re-executed!', ctx.obj.debug)

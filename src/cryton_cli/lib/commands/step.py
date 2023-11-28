import click
from typing import List, Optional

from cryton_cli.lib.util import api, util


# Step
@click.group('steps')
@click.pass_context
def step(_) -> None:
    """
    Manage Steps from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@step.command('list')
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('-o', '--offset', type=click.INT, default=0, help='The initial index from which to return the results.')
@click.option('-l', '--limit', type=click.INT, default=20, help='Number of results to return per page.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.option('-p', '--parent', type=click.INT, help='Filter Steps using Stage ID.')
@click.option('-f', '--filter', 'parameter_filters', type=click.STRING, multiple=True,
              help='Filter results using returned parameters (for example `id=1`, `name=test`, etc.).')
@click.pass_context
def step_list(ctx: click.Context, less: bool, offset: int, limit: int, localize: bool, parent: int, 
              parameter_filters: Optional[List[str]]) -> None:
    """
    List existing Steps in Cryton.

    \f
    :param ctx: Click ctx object
    :param less: Show less like output
    :param offset: Initial index from which to return the results
    :param limit: Number of results per page
    :param localize: If datetime variables should be converted to local timezone
    :param parent: Stage ID used to filter returned Steps
    :param parameter_filters: Filter results using returned parameters (for example `id`, `name`, etc.)
    :return: None
    """
    results_filter = "&".join(parameter_filters)
    appendix = f'?limit={limit}&offset={offset}&{results_filter}'
    custom_params = {}
    if parent is not None:
        custom_params.update({'stage_model_id': parent})
    response = api.get_request(ctx.obj.api_url, api.STEP_LIST + appendix, custom_params=custom_params)

    to_print = ['id', 'name', 'attack_module', 'attack_module_args', 'is_init', 'is_final', 'executor',
                'create_named_session', 'use_named_session', 'use_any_session_to_target', 'output_prefix']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@step.command('create')
@click.argument('stage_id', type=click.INT, required=True)
@click.argument('file', type=click.Path(exists=True), required=True)
@click.option('-i', '--inventory-file', 'inventory_files', type=click.Path(exists=True), multiple=True,
              help="Inventory file used to fill the template. Can be used multiple times.")
@click.pass_context
def step_create(ctx: click.Context, stage_id: int, file: str, inventory_files: list) -> None:
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
    with open(file, "rb") as f:
        files = {'file': f.read()}

    files.update(util.load_files(inventory_files))

    response = api.post_request(ctx.obj.api_url, api.STEP_CREATE, files=files, data={'stage_id': stage_id})

    util.echo_msg(response, 'Step successfully created!', ctx.obj.debug)


@step.command('show')
@click.argument('step_id', type=click.INT, required=True)
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.pass_context
def step_read(ctx: click.Context, step_id: int, less: bool, localize: bool) -> None:
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
    response = api.get_request(ctx.obj.api_url, api.STEP_READ, step_id)

    to_print = ['id', 'name', 'attack_module', 'attack_module_args', 'is_init', 'is_final', 'executor',
                'create_named_session', 'use_named_session', 'use_any_session_to_target', 'output_prefix']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@step.command('delete')
@click.argument('step_id', type=click.INT, required=True)
@click.pass_context
def step_delete(ctx: click.Context, step_id: int) -> None:
    """
    Delete Step with STEP_ID saved in Cryton.

    STEP_ID is ID of the Step you want to delete.

    \f
    :param ctx: Click ctx object
    :param step_id: ID of the desired Step
    :return: None
    """
    response = api.delete_request(ctx.obj.api_url, api.STEP_DELETE, step_id)

    util.echo_msg(response, 'Step successfully deleted!', ctx.obj.debug)


@step.command('validate')
@click.argument('file', type=click.Path(exists=True), required=True)
@click.option('-i', '--inventory-file', 'inventory_files', type=click.Path(exists=True), multiple=True,
              help="Inventory file used to fill the template. Can be used multiple times.")
@click.pass_context
def step_validate(ctx: click.Context, file: str, inventory_files: list) -> None:
    """
    Validate (syntax check) your FILE with Step.

    FILE is path/to/your/file that you want to validate.

    \f
    :param ctx: Click ctx object
    :param file: File containing your Step in yaml
    :param inventory_files: Inventory file(s) used to fill the template
    :return: None
    """
    with open(file, "rb") as f:
        files = {'file': f.read()}

    files.update(util.load_files(inventory_files))

    response = api.post_request(ctx.obj.api_url, api.STEP_VALIDATE, files=files)

    util.echo_msg(response, 'Step successfully validated!', ctx.obj.debug)


@step.command('execute')
@click.argument('step_id', type=click.INT, required=True)
@click.argument('stage_execution_id', type=click.INT, required=True)
@click.pass_context
def step_execute(ctx: click.Context, step_id: int, stage_execution_id: int) -> None:
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
    arguments = {'stage_execution_id': stage_execution_id}
    response = api.post_request(ctx.obj.api_url, api.STEP_EXECUTE, step_id, custom_dict=arguments)

    util.echo_msg(response, 'Step successfully executed!', ctx.obj.debug)


# StepExecution
@click.group('step-executions')
@click.pass_context
def step_execution(_) -> None:
    """
    Manage Step's executions from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@step_execution.command('list')
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('-o', '--offset', type=click.INT, default=0, help='The initial index from which to return the results.')
@click.option('-l', '--limit', type=click.INT, default=20, help='Number of results to return per page.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.option('-p', '--parent', type=click.INT, help='Filter Step executions using Stage execution ID.')
@click.option('-f', '--filter', 'parameter_filters', type=click.STRING, multiple=True,
              help='Filter results using returned parameters (for example `id=1`, `name=test`, etc.).')
@click.pass_context
def step_execution_list(ctx: click.Context, less: bool, offset: int, limit: int, localize: bool, parent: int, 
                        parameter_filters: Optional[List[str]]) -> None:
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
    results_filter = "&".join(parameter_filters)
    appendix = f'?limit={limit}&offset={offset}&{results_filter}'
    custom_params = {}
    if parent is not None:
        custom_params.update({'stage_execution_id': parent})
    response = api.get_request(ctx.obj.api_url, api.STEP_EXECUTION_LIST + appendix, custom_params=custom_params)

    to_print = ['id', 'start_time', 'pause_time', 'finish_time', 'state', 'result', 'evidence_file', 'parent_id',
                'valid']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@step_execution.command('delete')
@click.argument('execution_id', type=click.INT, required=True)
@click.pass_context
def step_execution_delete(ctx: click.Context, execution_id: int) -> None:
    """
    Delete Step's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Step's execution you want to delete.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Step's execution
    :return: None
    """
    response = api.delete_request(ctx.obj.api_url, api.STEP_EXECUTION_DELETE, execution_id)

    util.echo_msg(response, 'Step execution successfully deleted!', ctx.obj.debug)


@step_execution.command('show')
@click.argument('execution_id', type=click.INT, required=True)
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.pass_context
def step_execution_read(ctx: click.Context, execution_id: int, less: bool, localize: bool) -> None:
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
    response = api.get_request(ctx.obj.api_url, api.STEP_EXECUTION_READ, execution_id)

    to_print = ['id', 'start_time', 'pause_time', 'finish_time', 'state', 'result', 'evidence_file', 'parent_id',
                'valid', 'mod_out', 'mod_err', 'std_out', 'std_err']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@step_execution.command('report')
@click.argument('execution_id', type=click.INT, required=True)
@click.option('-f', '--file', type=click.Path(exists=True), default='/tmp',
              help='File to save the report to (default is /tmp).')
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.pass_context
def step_execution_report(ctx: click.Context, execution_id: int, file: str, less: bool, localize: bool) -> None:
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
    response = api.get_request(ctx.obj.api_url, api.STEP_EXECUTION_REPORT, execution_id)

    util.get_yaml(response, file, f'report-step-execution_{execution_id}', less, less, localize, ctx.obj.debug)


@step_execution.command('kill')
@click.argument('execution_id', type=click.INT, required=True)
@click.pass_context
def step_execution_kill(ctx: click.Context, execution_id: int) -> None:
    """
    Kill Step's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Step's execution you want to kill.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Step's execution
    :return: None
    """
    response = api.post_request(ctx.obj.api_url, api.STEP_EXECUTION_KILL, execution_id)

    util.echo_msg(response, 'Step execution successfully killed!', ctx.obj.debug)


@step_execution.command('re-execute')
@click.argument('execution_id', type=click.INT, required=True)
@click.pass_context
def step_execution_re_execute(ctx: click.Context, execution_id: int) -> None:
    """
    Re-execute Step's execution with EXECUTION_ID saved in Cryton.

    EXECUTION_ID is ID of the Step's execution you want to kill.

    \f
    :param ctx: Click ctx object
    :param execution_id: ID of the desired Step's execution
    :return: None
    """
    response = api.post_request(ctx.obj.api_url, api.STEP_EXECUTION_RE_EXECUTE, execution_id)

    util.echo_msg(response, 'Step execution successfully re-executed!', ctx.obj.debug)

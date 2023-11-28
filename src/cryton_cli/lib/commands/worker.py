import click
from typing import List, Optional

from cryton_cli.lib.util import api, util


# Worker
@click.group('workers')
@click.pass_context
def worker(_) -> None:
    """
    Manage Workers from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@worker.command('list')
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('-o', '--offset', type=click.INT, default=0, help='The initial index from which to return the results.')
@click.option('-l', '--limit', type=click.INT, default=20, help='Number of results to return per page.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.option('-f', '--filter', 'parameter_filters', type=click.STRING, multiple=True,
              help='Filter results using returned parameters (for example `id=1`, `name=test`, etc.).')
@click.pass_context
def worker_list(ctx: click.Context, less: bool, offset: int, limit: int, localize: bool,
                parameter_filters: Optional[List[str]]) -> None:
    """
    List existing Workers in Cryton.

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
    response = api.get_request(ctx.obj.api_url, api.WORKER_LIST + appendix)

    to_print = ['id', 'name', 'description', 'state']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@worker.command('create')
@click.argument('name', type=click.STRING, required=True)
@click.option('-d', '--description', type=click.STRING, help='Description of your Worker (wrap in "").', default="")
@click.option('-f', '--force', is_flag=True, help="Ignore, if Worker with the same parameter 'name' exists.")
@click.pass_context
def worker_create(ctx: click.Context, name: str, description: str, force: bool) -> None:
    """
    Create new Worker with NAME and save it into Cryton.

    NAME of your Worker (will be used to match your Worker). For example: "MyCustomName".

    \f
    :param ctx: Click ctx object
    :param name: Custom name for Worker
    :param description: Worker's description
    :param force: If Worker with the same name exists, create a new one anyway
    :return: None
    """
    arguments = {'name': name, 'description': description, 'force': force}
    response = api.post_request(ctx.obj.api_url, api.WORKER_CREATE, custom_dict=arguments)

    util.echo_msg(response, 'Worker successfully created!', ctx.obj.debug)


@worker.command('show')
@click.argument('worker_id', type=click.INT, required=True)
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.pass_context
def worker_read(ctx: click.Context, worker_id: int, less: bool, localize: bool) -> None:
    """
    Show Worker with WORKER_ID saved in Cryton.

    WORKER_ID is ID of the Worker you want to see.

    \f
    :param ctx: Click ctx object
    :param worker_id: ID of the desired Worker
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = api.get_request(ctx.obj.api_url, api.WORKER_READ, worker_id)

    to_print = ['id', 'name', 'description', 'state']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@worker.command('delete')
@click.argument('worker_id', type=click.INT, required=True)
@click.pass_context
def worker_delete(ctx: click.Context, worker_id: int) -> None:
    """
    Delete Worker with WORKER_ID saved in Cryton.

    WORKER_ID is ID of the Worker you want to delete.

    \f
    :param ctx: Click ctx object
    :param worker_id: ID of the desired Worker
    :return: None
    """
    response = api.delete_request(ctx.obj.api_url, api.WORKER_DELETE, worker_id)

    util.echo_msg(response, 'Worker successfully deleted!', ctx.obj.debug)


@worker.command('health-check')
@click.argument('worker_id', type=click.INT, required=True)
@click.pass_context
def worker_health_check(ctx: click.Context, worker_id: int) -> None:
    """
    Check if Worker with WORKER_ID saved in Cryton is online.

    WORKER_ID is ID of the Worker you want to check.

    \f
    :param ctx: Click ctx object
    :param worker_id: ID of the desired Worker
    :return: None
    """
    response = api.post_request(ctx.obj.api_url, api.WORKER_HEALTH_CHECK, worker_id)
    util.echo_msg(response, 'Worker successfully checked!', ctx.obj.debug)

import click
from typing import Union

from cryton.cli.utility import helpers
from cryton.cli.utility.decorators import *
from cryton.cli.config import Worker


# Worker
@click.group("workers")
@click.pass_context
def worker(_) -> None:
    """
    Manage Workers from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@worker.command("list")
@click.pass_context
@common_list_decorators
def worker_list(
    ctx: helpers.Context,
    less: bool,
    offset: int,
    limit: int,
    localize: bool,
    parameter_filters: tuple[tuple[str, Union[str, int]]],
) -> None:
    """
    List existing Workers.

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
    include = ["id", "name", "description", "state"]
    ctx.obj.get_items(Worker.LIST, offset, limit, additional_parameters, include, less, localize)


@worker.command("create")
@click.pass_context
@click.argument("name", type=click.STRING, required=True)
@click.option("-d", "--description", type=click.STRING, help='Description of your Worker (wrap in "").', default="")
@click.option("-f", "--force", is_flag=True, help="Ignore, if Worker with the same parameter 'name' exists.")
def worker_create(ctx: helpers.Context, name: str, description: str, force: bool) -> None:
    """
    Create new Worker with NAME.

    NAME of your Worker (will be used to match your Worker). For example: "MyCustomName".

    \f
    :param ctx: Click ctx object
    :param name: Custom name for Worker
    :param description: Worker's description
    :param force: If Worker with the same name exists, create a new one anyway
    :return: None
    """
    arguments = {"name": name, "description": description, "force": force}
    response = ctx.obj.api_post(Worker.CREATE, json=arguments)
    helpers.print_message(response, ctx.obj.debug)


@worker.command("show")
@click.pass_context
@click.argument("worker_id", type=click.INT, required=True)
@d_less
@d_localize
def worker_read(ctx: helpers.Context, worker_id: int, less: bool, localize: bool) -> None:
    """
    Show Worker with WORKER_ID.

    WORKER_ID is ID of the Worker you want to see.

    \f
    :param ctx: Click ctx object
    :param worker_id: ID of the desired Worker
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(Worker.READ, worker_id)
    include = ["id", "name", "description", "state"]
    helpers.print_items(response, include, less, localize, ctx.obj.debug)


@worker.command("delete")
@click.pass_context
@click.argument("worker_id", type=click.INT, required=True)
def worker_delete(ctx: helpers.Context, worker_id: int) -> None:
    """
    Delete Worker with WORKER_ID saved in Cryton.

    WORKER_ID is ID of the Worker you want to delete.

    \f
    :param ctx: Click ctx object
    :param worker_id: ID of the desired Worker
    :return: None
    """
    ctx.obj.delete_item(Worker.DELETE, worker_id)


@worker.command("health-check")
@click.pass_context
@click.argument("worker_id", type=click.INT, required=True)
def worker_health_check(ctx: helpers.Context, worker_id: int) -> None:
    """
    Check if Worker with WORKER_ID is online.

    WORKER_ID is ID of the Worker you want to check.

    \f
    :param ctx: Click ctx object
    :param worker_id: ID of the desired Worker
    :return: None
    """
    response = ctx.obj.api_post(Worker.HEALTH_CHECK, worker_id)
    helpers.print_message(response, ctx.obj.debug)

import click
from typing import Union

from cryton.cli.utility import helpers
from cryton.cli.utility.decorators import *
from cryton.cli.config import Template


@click.group("plan-templates")  # TODO: change to templates
@click.pass_context
def template(_) -> None:
    """
    Manage Plan templates from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@template.command("list")
@click.pass_context
@common_list_decorators
def template_list(
    ctx: helpers.Context,
    less: bool,
    offset: int,
    limit: int,
    localize: bool,
    parameter_filters: tuple[tuple[str, Union[str, int]]],
) -> None:
    """
    List existing Plan templates in Cryton.

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
    include = ["id", "file"]
    ctx.obj.get_items(Template.LIST, offset, limit, additional_parameters, include, less, localize)


@template.command("create")
@click.pass_context
@click.argument("file", type=click.Path(exists=True), required=True)
def template_create(ctx: helpers.Context, file: str) -> None:
    """
    Store Plan Template into Cryton.

    FILE is path/to/your/file that you want to upload to Cryton.

    \f
    :param ctx: Click ctx object
    :param file: File containing your Plan Template in yaml
    :return: None
    """
    with open(file) as fp:
        files = {"file": fp}
        response = ctx.obj.api_post(Template.CREATE, files=files)
    helpers.print_message(response, ctx.obj.debug)


@template.command("show")  # TODO: rename `show` to something else?
@click.pass_context
@click.argument("template_id", type=click.INT, required=True)
@d_less
@d_localize
def template_read(ctx: helpers.Context, template_id: int, less: bool, localize: bool) -> None:
    """
    Show Template with TEMPLATE_ID saved in Cryton.

    TEMPLATE_ID is ID of the Template you want to see.

    \f
    :param ctx: Click ctx object
    :param template_id: ID of the desired Template
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(Template.READ, template_id)
    include = ["id", "file"]
    helpers.print_items(response, include, less, localize, ctx.obj.debug)


@template.command("delete")
@click.pass_context
@click.argument("template_id", type=click.INT, required=True)
def template_delete(ctx: helpers.Context, template_id: int) -> None:
    """
    Delete Template with TEMPLATE_ID saved in Cryton.

    TEMPLATE_ID is ID of the Template you want to delete.

    \f
    :param ctx: Click ctx object
    :param template_id: ID of the desired Template
    :return: None
    """
    ctx.obj.delete_item(Template.DELETE, template_id)


@template.command("get-template")
@click.pass_context
@click.argument("template_id", type=click.INT, required=True)
@d_save_report
@d_less
@d_localize
def template_get_template(ctx: helpers.Context, template_id: int, file: str, less: bool, localize: bool) -> None:
    """
    Get Template with TEMPLATE_ID saved in Cryton.

    TEMPLATE_ID is ID of the Template you want to get.

    \f
    :param ctx: Click ctx object
    :param template_id: ID of the desired Template
    :param file: File to save the template to
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = ctx.obj.api_get(Template.GET_TEMPLATE, template_id)
    helpers.save_yaml(response, file, f"template-{template_id}.yml", less, less, localize, ctx.obj.debug)

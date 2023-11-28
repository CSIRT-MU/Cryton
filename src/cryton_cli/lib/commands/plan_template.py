import click
from typing import List, Optional

from cryton_cli.lib.util import api, util


# Plan Template
@click.group('plan-templates')
@click.pass_context
def template(_) -> None:
    """
    Manage Plan templates from here.

    \f
    :param _: Click ctx object
    :return: None
    """


@template.command('list')
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('-o', '--offset', type=click.INT, default=0, help='The initial index from which to return the results.')
@click.option('-l', '--limit', type=click.INT, default=20, help='Number of results to return per page.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.option('-f', '--filter', 'parameter_filters', type=click.STRING, multiple=True,
              help='Filter results using returned parameters (for example `id=1`, `name=test`, etc.).')
@click.pass_context
def template_list(ctx: click.Context, less: bool, offset: int, limit: int, localize: bool, 
                  parameter_filters: Optional[List[str]]) -> None:
    """
    List existing Plan templates in Cryton.

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
    response = api.get_request(ctx.obj.api_url, api.TEMPLATE_LIST + appendix)

    to_print = ['id', 'file']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@template.command('create')
@click.argument('file', type=click.Path(exists=True), required=True)
@click.pass_context
def template_create(ctx: click.Context, file: str) -> None:
    """
    Store Plan Template into Cryton.

    FILE is path/to/your/file that you want to upload to Cryton.

    \f
    :param ctx: Click ctx object
    :param file: File containing your Plan Template in yaml
    :return: None
    """

    with open(file) as fp:
        arguments = {'file': fp}
        response = api.post_request(ctx.obj.api_url, api.TEMPLATE_CREATE, files=arguments)

    util.echo_msg(response, 'Template successfully created!', ctx.obj.debug)


@template.command('show')
@click.argument('template_id', type=click.INT, required=True)
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.pass_context
def template_read(ctx: click.Context, template_id: int, less: bool, localize: bool) -> None:
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
    response = api.get_request(ctx.obj.api_url, api.TEMPLATE_READ, template_id)

    to_print = ['id', 'file']

    util.echo_list(response, to_print, less, localize, ctx.obj.debug)


@template.command('delete')
@click.argument('template_id', type=click.INT, required=True)
@click.pass_context
def template_delete(ctx: click.Context, template_id: int) -> None:
    """
    Delete Template with TEMPLATE_ID saved in Cryton.

    TEMPLATE_ID is ID of the Template you want to delete.

    \f
    :param ctx: Click ctx object
    :param template_id: ID of the desired Template
    :return: None
    """
    response = api.delete_request(ctx.obj.api_url, api.TEMPLATE_DELETE, template_id)

    util.echo_msg(response, 'Template successfully deleted!', ctx.obj.debug)


@template.command('get-template')
@click.argument('template_id', type=click.INT, required=True)
@click.option('-f', '--file', type=click.Path(exists=True), default='/tmp',
              help='File to save the template to (default is /tmp).')
@click.option('--less', is_flag=True, help='Show less like output.')
@click.option('--localize', is_flag=True, help='Convert UTC datetime to local timezone.')
@click.pass_context
def template_get_template(ctx: click.Context, template_id: int, file: str, less: bool, localize: bool) -> None:
    """
    Get Template with TEMPLATE_ID saved in Cryton.

    TEMPLATE_ID is ID of the Template you want to get.

    \f
    :param ctx: Click ctx object
    :param template_id: ID of the desired Template
    :param file: File to save the template to (default is /tmp)
    :param less: Show less like output
    :param localize: If datetime variables should be converted to local timezone
    :return: None
    """
    response = api.get_request(ctx.obj.api_url, api.TEMPLATE_GET_TEMPLATE, template_id)

    util.get_yaml(response, file, f'plan-template_{template_id}', less, less, localize, ctx.obj.debug)

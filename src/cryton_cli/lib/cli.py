import click

from cryton_cli.lib.util import util
from cryton_cli.lib.commands import plan_template, run, plan, step, worker, execution_variable, stage, log


@click.group()
@click.option('-H', '--host', type=click.STRING, help='Set Cryton\'s address (default is localhost).')
@click.option('-p', '--port', type=click.INT, help='Set Cryton\'s address (default is 8000).')
@click.option('--secure', is_flag=True, help='Set if HTTPS will be used.')
@click.option('--debug', is_flag=True, help='Show non formatted raw output.')
@click.version_option(message=f"%(prog)s, version %(version)s")
@click.pass_context
def cli(ctx: click.Context, host: str, port: int, secure: bool, debug: bool) -> None:
    """
    A CLI wrapper for Cryton API.

    \f
    :param ctx: Click context
    :param secure: True if use HTTPS for requests, else HTTP (default is False)
    :param debug: Show non formatted raw output
    :param host: Cryton's REST API url (default is None)
    :param port: Cryton's REST API port (default is None)
    :return: None
    """
    ctx.obj = util.CliContext(host, port, secure, debug)


cli.add_command(run.run)
cli.add_command(plan.plan)
cli.add_command(plan.plan_execution)
cli.add_command(stage.stage)
cli.add_command(stage.stage_execution)
cli.add_command(step.step)
cli.add_command(step.step_execution)
cli.add_command(worker.worker)
cli.add_command(plan_template.template)
cli.add_command(execution_variable.execution_variable)
cli.add_command(log.log)


@cli.command('generate-docs')
@click.argument('file', type=click.Path(), required=True)
@click.option('-l', '--layer', type=click.INT, help='Highest header level.', default=2)
def generate_docs(file: str, layer: int):
    """
    Generate Markdown documentation for CLI.

    FILE is path/to/your/file where you want to save the generated documentation.

    \f
    :param file: Where to save the generated documentation
    :param layer: Highest header level
    :return: None
    """
    ctx = click.Context(cli, info_name=cli.name, parent=None)
    docs = ''
    for cmd_detail in cli.to_info_dict(ctx).get('commands').values():
        docs += util.render_documentation(cmd_detail, layer)
    docs = util.clean_up_documentation(docs)

    if file is not None:
        try:
            with open(file, 'w+') as f:
                f.write(docs)
        except IOError:
            click.echo(f"Cannot access {file}.")
            return

    click.echo(f"Documentation saved in {file}.")

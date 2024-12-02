import click

from cryton.cli.utility import helpers
from cryton.cli.config import SETTINGS
from cryton.cli.commands import plan_template, run, plan, step, worker, execution_variable, stage, log


@click.group()
@click.pass_context
@click.version_option(message=f"%(version)s")
@click.option("-H", "--host", type=click.STRING, help="Cryton's API address.")
@click.option("-p", "--port", type=click.INT, help="Cryton's API address.")
@click.option("--secure", is_flag=True, help="Use HTTPS instead of HTTP.")
@click.option("--debug", is_flag=True, help="Do not format output.")
def cli(ctx: click.Context, host: str | None, port: int | None, secure: bool, debug: bool) -> None:
    """
    Wrapper for Hive's REST API.

    \f
    :param ctx: Click context
    :param host: Cryton's REST API url
    :param port: Cryton's REST API port
    :param secure: If True, use HTTPS for requests else HTTP
    :param debug: Do not format output
    :return: None
    """
    ctx.obj = helpers.CLIContext(
        host or SETTINGS.api.host,
        port or SETTINGS.api.port,
        True if SETTINGS.api.ssl and not secure else secure,
        True if SETTINGS.debug and not debug else debug,
    )


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


@cli.command("generate-docs")
@click.pass_context
@click.argument("file", type=click.Path(), required=True)
@click.option("-l", "--layer", type=click.INT, help="Highest header level.", default=2)
def generate_docs(ctx: helpers.Context, file: str, layer: int):
    """
    Generate Markdown documentation for CLI.

    FILE is path/to/your/file where you want to save the generated documentation.

    \f
    :param ctx: Click context
    :param file: Where to save the generated documentation
    :param layer: Highest header level
    :return: None
    """
    docs = ""
    for cmd_detail in ctx.parent.to_info_dict().get("command").get("commands").values():
        docs += helpers.render_documentation(cmd_detail, layer)
    docs = helpers.clean_up_documentation(docs)

    if file is not None:
        try:
            with open(file, "w+") as f:
                f.write(docs)
        except IOError:
            click.echo(f"Cannot access {file}.")
            return

    click.echo(f"Documentation saved in {file}.")

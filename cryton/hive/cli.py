import sys
import click

from cryton.hive.manage import main


@click.group()
@click.version_option()
def cli() -> None:
    """
    Cryton Hive.

    \f
    :return: None
    """
    pass


@cli.command("django", context_settings=dict(allow_extra_args=True))
def django():
    """
    Django CLI wrapper. Type `cryton-hive django help` for help.

    \f
    :return: None
    """
    main()


@cli.command("start")
@click.pass_context
@click.option("-m", "--migrate-database", is_flag=True, help="")
@click.option("-b", "--bind", type=click.STRING, default="0.0.0.0:8000", help="ADDRESS:PORT to serve the server at.")
@click.option("-w", "--workers", type=click.INT, default=2, help="NUMBER of worker processes for handling requests.")
def start(ctx: click.Context, migrate_database: bool, bind: str, workers: int) -> None:
    """
    Start hive.

    \f
    :param ctx: Click context
    :param migrate_database:
    :param bind:
    :param workers:
    :return: None
    """
    argv = sys.argv
    if migrate_database:
        sys.argv = [argv[0], "django", "migrate"]
        ctx.invoke(django)

    sys.argv = [argv[0], "django", "start", "--bind", bind, "--workers", str(workers)]
    ctx.invoke(django)

import click
import pyfiglet

from cryton.worker.config.settings import SETTINGS
from cryton.worker import worker
from cryton.worker.utility import util


@click.group()
@click.version_option()
def cli() -> None:
    """
    Cryton Worker.

    \f
    :return: None
    """
    pass


@cli.command("start")
@click.option(
    "-Ru",
    "--rabbit-username",
    type=click.STRING,
    default=SETTINGS.rabbit.username,
    show_default=True,
    help="Rabbit login username.",
)
@click.option(
    "-Rp",
    "--rabbit-password",
    type=click.STRING,
    default=SETTINGS.rabbit.password,
    show_default=True,
    help="Rabbit login password.",
)
@click.option(
    "-Rh",
    "--rabbit-host",
    type=click.STRING,
    default=SETTINGS.rabbit.host,
    show_default=True,
    help="Rabbit server host.",
)
@click.option(
    "-RP", "--rabbit-port", type=click.INT, default=SETTINGS.rabbit.port, show_default=True, help="Rabbit server port."
)
@click.option(
    "-n",
    "--name",
    type=click.STRING,
    default=SETTINGS.name,
    show_default=True,
    help="What name should the Worker use (will be used to match your Worker).",
)
@click.option(
    "-cc",
    "--consumer-count",
    type=click.INT,
    default=SETTINGS.consumer_count,
    show_default=True,
    help="Consumers to use for queues. (higher == faster message consuming, heavier processor usage)",
)
@click.option(
    "-mr",
    "--max-retries",
    type=click.INT,
    default=SETTINGS.max_retries,
    show_default=True,
    help="How many times to try to connect.",
)
@click.option("-P", "--persistent", is_flag=True, help="If Worker should stay alive and keep on trying forever.")
def start_worker(
    rabbit_username: str,
    rabbit_password: str,
    persistent: bool,
    rabbit_host: str,
    rabbit_port: int,
    name: str,
    consumer_count: int,
    max_retries: int,
) -> None:
    """
    Start worker and optionally install requirements.

    \f
    :param consumer_count: How many consumers to use for queues
    (higher == faster RabbitMQ requests consuming, but heavier processor usage)
    :param name: Worker name (prefix) for queues
    :param rabbit_host: Rabbit's server port
    :param rabbit_port: Rabbit's server host
    :param rabbit_username: Rabbit's username
    :param rabbit_password: Rabbit's password
    :param max_retries: How many times to try to connect
    :param persistent: Keep Worker alive and keep on trying forever (if True)
    :return: None
    """
    pyfiglet.print_figlet("Worker", "graffiti", "RED")
    worker_obj = worker.Worker(
        rabbit_host,
        rabbit_port,
        rabbit_username,
        rabbit_password,
        name,
        consumer_count,
        consumer_count,
        max_retries,
        persistent,
    )
    worker_obj.start()

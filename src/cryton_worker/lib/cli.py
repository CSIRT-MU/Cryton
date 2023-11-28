import click
import pyfiglet

from cryton_worker.etc import config
from cryton_worker.lib import worker
from cryton_worker.lib.util import util


@click.group()
@click.version_option()
def cli() -> None:
    """
    Cryton Worker CLI.

    \f
    :return: None
    """
    pass


@cli.command("start")
@click.option("-I", "--install-requirements", is_flag=True,
              help="Install Python requirements from each requirements.txt in modules_dir.")
@click.option("-Ru", "--rabbit-username", type=click.STRING, default=config.RABBIT_USERNAME, show_default=True,
              help="Rabbit login username.")
@click.option("-Rp", "--rabbit-password", type=click.STRING, default=config.RABBIT_PASSWORD, show_default=True,
              help="Rabbit login password.")
@click.option("-Rh", "--rabbit-host", type=click.STRING, default=config.RABBIT_HOST, show_default=True,
              help="Rabbit server host.")
@click.option("-RP", "--rabbit-port", type=click.INT, default=config.RABBIT_PORT, show_default=True,
              help="Rabbit server port.")
@click.option("-n", "--name", type=click.STRING, default=config.WORKER_NAME, show_default=True,
              help="What name should the Worker use (will be used to match your Worker).")
@click.option("-cc", "--consumer-count", type=click.INT, default=config.CONSUMER_COUNT, show_default=True,
              help="Consumers to use for queues. (higher == faster message consuming, heavier processor usage)")
@click.option("-pc", "--processor-count", type=click.INT, default=config.PROCESSOR_COUNT, show_default=True,
              help="Processors to use for internal requests (higher == more responsive, heavier processor usage).")
@click.option("-mr", "--max-retries", type=click.INT, default=config.MAX_RETRIES, show_default=True,
              help="How many times to try to connect.")
@click.option("-P", "--persistent", is_flag=True, help="If Worker should stay alive and keep on trying forever.")
def start_worker(install_requirements: bool, rabbit_username: str, rabbit_password: str, persistent: bool,
                 rabbit_host: str, rabbit_port: int, name: str, consumer_count: int, processor_count: int,
                 max_retries: int) -> None:
    """
    Start worker and optionally install requirements.

    \f
    :param consumer_count: How many consumers to use for queues
    (higher == faster RabbitMQ requests consuming, but heavier processor usage)
    :param processor_count: How many processors to use for internal requests
    (higher == more responsive internal requests processing, but heavier processor usage)
    :param name: Worker name (prefix) for queues
    :param rabbit_host: Rabbit's server port
    :param rabbit_port: Rabbit's server host
    :param rabbit_username: Rabbit's username
    :param rabbit_password: Rabbit's password
    :param max_retries: How many times to try to connect
    :param persistent: Keep Worker alive and keep on trying forever (if True)
    :param install_requirements: Install Python requirements from each 'requirements.txt' in modules_dir
    :return: None
    """
    pyfiglet.print_figlet("Worker", "graffiti", "RED")
    if install_requirements or config.INSTALL_REQUIREMENTS:
        click.echo("Checking and installing module requirements..", nl=False)
        util.install_modules_requirements(config.DEBUG)
        click.echo("OK")

    worker_obj = worker.Worker(rabbit_host, rabbit_port, rabbit_username, rabbit_password, name, consumer_count,
                               processor_count, max_retries, persistent)
    worker_obj.start()

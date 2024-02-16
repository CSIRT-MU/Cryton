import click
import time
from threading import Thread
from click import echo, secho

from cryton.hive.asgi import application
from cryton.hive.services.gunicorn import GunicornApplication
from cryton.hive.services.listener import Listener
from cryton.hive.utility.logger import logger_object


@click.group()
@click.version_option()
def cli() -> None:
    """
    Cryton Hive.

    \f
    :return: None
    """
    pass

    # TODO: create migrate command and add --migrate-database to the start command to invoke the migration command

@cli.command("start")
def start() -> None:
    # parser.add_argument("--bind", type=str, help="ADDRESS:PORT to serve the server at.")
    # parser.add_argument("--workers", type=int, help="The NUMBER of worker processes for handling requests.")
    """
    Start hive.

    \f
    :return: None
    """

    options = {}
    hard_options = {
        "bind": options.get("bind", "0.0.0.0:8000"),
        "worker_class": "uvicorn.workers.UvicornWorker",
        "workers": options.get("workers", 2),
        "loglevel": "warning"
    }

    echo("Starting REST API... ", nl=False)
    gunicorn_app = GunicornApplication(application, hard_options)
    gunicorn_app.start()
    echo("OK")

    echo("Starting RabbitMQ listener... ", nl=False)
    listener = Listener()
    listener.start(False)
    echo("OK")

    echo("Starting logger processor... ", nl=False)
    # Start log_handler in a thread to ensure the logs from multiprocessing aren't missing
    logger_processor_thread = Thread(target=logger_object.log_handler)
    logger_processor_thread.start()
    echo("OK")

    secho("Running!", fg="green")
    echo("To exit press CTRL+C")

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        pass

    echo("Stopping REST API... ", nl=False)
    gunicorn_app.stop()
    echo("OK")

    echo("Stopping RabbitMQ listener... ", nl=False)
    listener.stop()
    echo("OK")

    echo("Cleaning up... ", nl=False)
    logger_object.log_queue.put(None)  # Ensure the log_handler will stop
    echo("OK")

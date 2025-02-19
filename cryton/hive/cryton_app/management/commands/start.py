import time
from django.core.management.base import BaseCommand
from click import echo, secho

from cryton.hive.asgi import application
from cryton.hive.services.gunicorn import GunicornApplication
from cryton.hive.services.listener import Listener


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--bind", type=str, help="ADDRESS:PORT to serve the server at.")
        parser.add_argument("--workers", type=int, help="The NUMBER of worker processes for handling requests.")

    def handle(self, *args, **options):
        """
        Starts logger processor, listener, and gunicorn app.
        :param args: Arguments passed to the handle
        :param options: Options passed to the handle
        :return: None
        """
        hard_options = {
            "bind": options.get("bind", "0.0.0.0:8000"),
            "worker_class": "uvicorn.workers.UvicornWorker",
            "workers": options.get("workers", 2),
            "loglevel": "warning",
        }

        echo("Starting REST API... ", nl=False)
        gunicorn_app = GunicornApplication(application, hard_options)
        gunicorn_app.start()
        echo("OK")

        echo("Starting RabbitMQ listener... ", nl=False)
        listener = Listener()
        listener.start(False)
        echo("OK")

        secho("Cryton Hive is up and running!", fg="green")
        echo("To exit press CTRL+C")

        try:
            while True:
                time.sleep(999)
        except KeyboardInterrupt:
            pass

        echo("Stopping REST API... ", nl=False)
        gunicorn_app.stop()
        echo("OK")

        echo("Stopping RabbitMQ listener... ", nl=False)
        listener.stop()
        echo("OK")

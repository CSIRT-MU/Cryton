from threading import Thread
from django.core.management.base import BaseCommand

from cryton_core.asgi import application
from cryton_core.lib.services.gunicorn import GunicornApplication
from cryton_core.lib.util.logger import logger_object


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--bind", type=str, help="ADDRESS:PORT to serve the server at.")
        parser.add_argument("--workers", type=int, help="The NUMBER of worker processes for handling requests.")

    def handle(self, *args, **options):
        hard_options = {
            "bind": options.get("bind", "0.0.0.0:8000"),
            "worker_class": "uvicorn.workers.UvicornWorker",
            "workers": options.get("workers", 2)
        }

        gunicorn_app = GunicornApplication(application, hard_options)

        # Start log_handler in a thread to ensure the logs from multiprocessing aren't missing
        logger_processor_thread = Thread(target=logger_object.log_handler)
        logger_processor_thread.start()

        try:
            gunicorn_app.run()
        finally:  # Ensure the log_handler will stop
            logger_object.log_queue.put(None)

from threading import Thread

from django.core.management.commands.runserver import Command as CommandRunserver
from cryton_core.lib.util.logger import logger_object


class Command(CommandRunserver):
    def handle(self, *args, **options):
        # Start log_handler in a thread to ensure the logs from multiprocessing aren't missing
        logger_processor_thread = Thread(target=logger_object.log_handler)
        logger_processor_thread.start()

        options["use_reloader"] = False  # Current logging implementation prevents us to use the auto reloading feature

        try:
            super().handle(*args, **options)
        finally:  # Ensure the log_handler will stop
            logger_object.log_queue.put(None)

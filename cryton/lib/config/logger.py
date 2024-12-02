from os import path
import structlog
import logging
import logging.config
import logging.handlers
from multiprocessing import Process, Queue

from cryton.lib.config.settings import LOGS_DIRECTORY


# TODO: test and make sure it works with each app (hive/worker, possibly others)
class LoggerWrapper:
    name = "cryton"

    def __init__(self, is_production: bool = False):
        self.logger_amqpstorm = logging.getLogger("amqpstorm")
        self.logger_apscheduler = logging.getLogger("apscheduler")
        self.set_config()
        self.configure()

        self.logger_amqpstorm.propagate = True
        self.logger_apscheduler.propagate = True
        self.logger = structlog.get_logger(self.name)
        self.logger.setLevel(logging.DEBUG if not is_production else logging.INFO)

        self.log_queue = Queue()

    @property
    def file_name(self):
        return f"{self.name}.log"

    def log_handler(self):
        """
        Simple function that takes logs from Processes and handles them instead.
        :return: None
        """
        while True:
            record: logging.LogRecord = self.log_queue.get()
            if record is None:
                break

            self.logger.handle(record)

    @staticmethod
    def configure():
        # TODO: configure to run the logger as non json when running in docker or console in general?
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    def set_config(self):
        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {"simple": {"format": "%(message)s"}},
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "level": "DEBUG",
                        "formatter": "simple",
                        "stream": "ext://sys.stdout",
                    },
                    "file": {
                        "class": "logging.handlers.RotatingFileHandler",
                        "level": "DEBUG",
                        "formatter": "simple",
                        "filename": path.join(LOGS_DIRECTORY, self.file_name),
                        "maxBytes": 10485760,
                        "backupCount": 20,
                        "encoding": "utf8",
                    },
                },
                "root": {"level": "NOTSET", "handlers": [], "propagate": True},
                "loggers": {
                    f"{self.name}": {"level": "INFO", "handlers": ["prod_logger"], "propagate": True},
                    f"{self.name}-debug": {
                        "level": "DEBUG",
                        "handlers": ["debug_logger", "console"],
                        "propagate": True,
                    },
                    "cryton-hive-test": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
                },
            }
        )


class LoggedProcess(Process):
    def __init__(self, logg_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logg_queue = logg_queue

        queue_handler = logging.handlers.QueueHandler(self.logg_queue)
        root = structlog.getLogger()
        root.setLevel(logging.DEBUG)
        if not root.hasHandlers():
            root.addHandler(queue_handler)


logger = LoggerWrapper().logger

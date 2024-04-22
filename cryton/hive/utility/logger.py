import structlog
import logging.config
import logging.handlers
from multiprocessing import Process, Queue

from cryton.hive.utility import constants
from cryton.hive.config.settings import SETTINGS


class Logger:
    """
    Default logger
    """

    def __init__(self, logger_config):
        self.logger_config = logger_config
        self.logger_type = constants.LOGGER_CRYTON_PRODUCTION
        self.logger = None
        self.log_queue = Queue()

        if SETTINGS.debug:
            self.logger_type = constants.LOGGER_CRYTON_DEBUG
            self.logger = structlog.get_logger(self.logger_type)
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger = structlog.get_logger(self.logger_type)
            self.logger.setLevel(logging.INFO)

    @property
    def logger_type(self):
        return self._logger_type

    @logger_type.setter
    def logger_type(self, logger_type):
        if logger_type not in constants.VALID_CRYTON_LOGGERS:
            raise RuntimeError(f"Wrong logger provided, valid loggers are {constants.VALID_CRYTON_LOGGERS}")
        if logger_type == constants.LOGGER_CRYTON_DEBUG or logger_type == constants.LOGGER_CRYTON_TESTING:
            self.logger = structlog.get_logger(logger_type)
            self.logger.setLevel(logging.DEBUG)
            logging.getLogger("amqpstorm").propagate = True
            logging.getLogger("apscheduler").propagate = True
        elif logger_type == constants.LOGGER_CRYTON_PRODUCTION:
            logging.getLogger("amqpstorm").propagate = False
            logging.getLogger("apscheduler").propagate = False
            self.logger = structlog.get_logger(logger_type)
            self.logger.setLevel(logging.INFO)
        self._logger_type = logger_type

    @property
    def logger_config(self):
        return self._logger_config

    @logger_config.setter
    def logger_config(self, new_logger_config):
        self._logger_config = new_logger_config
        logging.config.dictConfig(new_logger_config)

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


class LoggedProcess(Process):
    def __init__(self, logg_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logg_queue = logg_queue

        queue_handler = logging.handlers.QueueHandler(self.logg_queue)
        root = structlog.getLogger()
        root.setLevel(logging.DEBUG)
        if not root.hasHandlers():
            root.addHandler(queue_handler)


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
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

config_dict = {
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
        "debug_logger": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": SETTINGS.log_file,
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8",
        },
        "prod_logger": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": SETTINGS.log_file,
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8",
        },
    },
    "root": {"level": "NOTSET", "handlers": [], "propagate": True},
    "loggers": {
        "cryton-hive": {"level": "INFO", "handlers": ["prod_logger"], "propagate": True},
        "cryton-hive-debug": {"level": "DEBUG", "handlers": ["debug_logger", "console"], "propagate": True},
        "cryton-hive-test": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
    },
}

logger_object = Logger(logger_config=config_dict)
logger = logger_object.logger

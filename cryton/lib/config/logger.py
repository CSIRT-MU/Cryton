from os import path
from uuid import uuid1
import structlog
import logging
import logging.config
import logging.handlers

from cryton.lib.config.settings import LOGS_DIRECTORY
from cryton.lib.utility.helpers import is_in_docker


class LoggerWrapper:
    def __init__(self, name: str, is_debug: bool):
        self._name = name
        self._is_debug = is_debug
        self._log_file_name = f"{self._name}-{uuid1()}.log"
        self._level = logging.DEBUG if self._is_debug else logging.INFO

        self._configure_logging()
        self._configure_structlog()

        self._logger: structlog.stdlib.BoundLogger = structlog.get_logger(self._name)

    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        return self._logger

    @property
    def log_file(self) -> str:
        return path.join(LOGS_DIRECTORY, self._log_file_name)

    def _configure_structlog(self) -> None:
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
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            wrapper_class=structlog.make_filtering_bound_logger(self._level),
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    def _configure_logging(self) -> None:
        handlers = ["file"]
        if self._is_debug or is_in_docker():
            handlers.append("console")

        # https://www.structlog.org/en/stable/standard-library.html
        pre_chain = [
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.ExtraAdder(),
            structlog.processors.TimeStamper(fmt="iso"),
        ]

        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "simple": {
                        "()": structlog.stdlib.ProcessorFormatter,
                        "processors": [
                            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                            structlog.processors.JSONRenderer(),
                        ],
                        "foreign_pre_chain": pre_chain,
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "level": "DEBUG",
                        "stream": "ext://sys.stdout",
                        "formatter": "simple",
                    },
                    "file": {
                        "class": "logging.handlers.RotatingFileHandler",
                        "level": "DEBUG",
                        "filename": self.log_file,
                        "maxBytes": 10485760,
                        "backupCount": 20,
                        "encoding": "utf8",
                        "formatter": "simple",
                    },
                },
                "root": {"level": "NOTSET", "handlers": handlers, "propagate": True},
                "loggers": {
                    f"{self._name}": {"level": "DEBUG", "handlers": [], "propagate": True},
                    "amqpstorm": {"level": "DEBUG", "handlers": [], "propagate": self._is_debug},
                    "apscheduler": {"level": "DEBUG", "handlers": [], "propagate": self._is_debug},
                    "urllib3": {"level": "DEBUG", "handlers": [], "propagate": self._is_debug},
                    "charset_normalizer": {"level": "DEBUG", "handlers": [], "propagate": self._is_debug},
                    "requests": {"level": "DEBUG", "handlers": [], "propagate": self._is_debug},
                    "dotenv": {"level": "DEBUG", "handlers": [], "propagate": self._is_debug},
                    "concurrent": {"level": "DEBUG", "handlers": [], "propagate": self._is_debug},
                    "asyncio": {"level": "DEBUG", "handlers": [], "propagate": self._is_debug},
                    "httpx": {"level": "DEBUG", "handlers": [], "propagate": self._is_debug},
                    "httpcore": {"level": "DEBUG", "handlers": [], "propagate": self._is_debug},
                    "django": {"level": "DEBUG", "handlers": [], "propagate": self._is_debug},
                },
            }
        )

import structlog
import logging.config

from cryton.worker.config.settings import SETTINGS

"""
Default Cryton Worker logger setup and configuration
"""

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
    "formatters": {
        "simple": {
            "format": "%(asctime)s.%(msecs)03d %(levelname)s [%(thread)d] {%(module)s} [%(funcName)s] %(message)s"
        }
    },
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
        "cryton-worker": {"level": "INFO", "handlers": ["prod_logger"], "propagate": True},
        "cryton-worker-debug": {"level": "DEBUG", "handlers": ["debug_logger", "console"], "propagate": True},
        "cryton-worker-test": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
    },
}

logging.config.dictConfig(config_dict)
amqpstorm_logger = logging.getLogger("amqpstorm")

logger = structlog.get_logger("cryton-worker-debug" if SETTINGS.debug else "cryton-worker")
logger.setLevel(logging.DEBUG if SETTINGS.debug else logging.INFO)
amqpstorm_logger.propagate = True if SETTINGS.debug else False

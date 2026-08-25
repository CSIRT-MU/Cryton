from cryton.lib.config.logger import LoggerWrapper
from cryton.worker.config.settings import SETTINGS


logger_wrapper = LoggerWrapper("cryton-worker", SETTINGS.debug)
logger = logger_wrapper.logger

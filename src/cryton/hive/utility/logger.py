from cryton.lib.config.logger import LoggerWrapper
from cryton.hive.config.settings import SETTINGS


logger_wrapper = LoggerWrapper("cryton-hive", SETTINGS.debug)
logger = logger_wrapper.logger

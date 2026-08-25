from dataclasses import dataclass
from os import getenv
from tzlocal import get_localzone_name

from cryton.lib.config.settings import SETTINGS_CLI, getenv_bool, getenv_int


@dataclass
class SettingsAPI:
    host: str
    port: int
    ssl: bool

    def __init__(self, raw_settings: dict):
        self.host = getenv("CRYTON_CLI_API_HOST", raw_settings.get("host", "127.0.0.1"))
        self.port = getenv_int("CRYTON_CLI_API_PORT", raw_settings.get("port", 8000))
        self.ssl = getenv_bool("CRYTON_CLI_API_SSL", raw_settings.get("ssl", False))


@dataclass
class Settings:
    api: SettingsAPI
    timezone: str
    debug: bool

    def __init__(self, raw_settings: dict):
        timezone = getenv("CRYTON_CLI_TIMEZONE", raw_settings.get("timezone", "default"))

        self.timezone = get_localzone_name() if timezone.lower() == "default" else timezone
        self.debug = getenv_bool("CRYTON_CLI_DEBUG", raw_settings.get("debug", False))
        self.api = SettingsAPI(raw_settings.get("api", {}))


SETTINGS = Settings(SETTINGS_CLI)

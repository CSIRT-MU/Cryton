from dataclasses import dataclass
from os import getenv, path

from cryton.lib.config.settings import SETTINGS_WORKER, getenv_bool, getenv_int, LOG_DIRECTORY, MODULES_DIRECTORY


@dataclass
class SettingsRabbit:
    host: str
    port: int
    username: str
    password: str

    def __init__(self, raw_settings: dict):
        self.host = getenv("CRYTON_WORKER_RABBIT_HOST", raw_settings.get("host", "127.0.0.1"))
        self.port = getenv_int("CRYTON_WORKER_RABBIT_PORT", raw_settings.get("port", 5672))
        self.username = getenv("CRYTON_WORKER_RABBIT_USERNAME", raw_settings.get("username", "cryton"))
        self.password = getenv("CRYTON_WORKER_RABBIT_PASSWORD", raw_settings.get("password", "cryton"))


class SettingsMetasploit:
    host: str
    port: int
    username: str
    password: str
    ssl: bool

    def __init__(self, raw_settings: dict):
        self.host = getenv("CRYTON_WORKER_METASPLOIT_HOST", raw_settings.get("host", "127.0.0.1"))
        self.port = getenv_int("CRYTON_WORKER_METASPLOIT_PORT", raw_settings.get("port", 55553))
        self.username = getenv("CRYTON_WORKER_METASPLOIT_USERNAME", raw_settings.get("username", "cryton"))
        self.password = getenv("CRYTON_WORKER_METASPLOIT_PASSWORD", raw_settings.get("password", "cryton"))
        self.ssl = getenv_bool("CRYTON_WORKER_METASPLOIT_SSL", raw_settings.get("ssl", True))


@dataclass
class SettingsEmpire:
    host: str
    port: int
    username: str
    password: str

    def __init__(self, raw_settings: dict):
        self.host = getenv("CRYTON_WORKER_EMPIRE_HOST", raw_settings.get("host", "127.0.0.1"))
        self.port = getenv_int("CRYTON_WORKER_EMPIRE_PORT", raw_settings.get("port", 1337))
        self.username = getenv("CRYTON_WORKER_EMPIRE_USERNAME", raw_settings.get("username", "cryton"))
        self.password = getenv("CRYTON_WORKER_EMPIRE_PASSWORD", raw_settings.get("password", "cryton"))


@dataclass
class SettingsModules:
    # TODO: can be removed, currently unused
    # TODO: would be cool if the user specified the modules he wanted and cryton installed them for the user on startup
    # TODO: use install_requirements for the installation of system requirements?
    #  each module could implement install_requirements method which would do that
    directory: str
    install_requirements: bool

    def __init__(self, raw_settings: dict):
        self.directory = MODULES_DIRECTORY
        self.install_requirements = getenv_bool(
            "CRYTON_WORKER_MODULES_INSTALL_REQUIREMENTS", raw_settings.get("install_requirements", True)
        )


@dataclass
class Settings:
    name: str
    debug: bool
    consumer_count: int  # TODO: rename
    max_retries: int
    log_file: str
    modules: SettingsModules
    rabbit: SettingsRabbit
    empire: SettingsEmpire
    metasploit: SettingsMetasploit

    def __init__(self, raw_settings: dict):
        self.name = getenv("CRYTON_WORKER_NAME", raw_settings.get("name", "worker"))  # TODO: by default use uuid?
        self.debug = getenv_bool("CRYTON_WORKER_DEBUG", raw_settings.get("debug", False))
        self.consumer_count = getenv_int("CRYTON_WORKER_CONSUMER_COUNT", raw_settings.get("consumer_count", 7))
        self.max_retries = getenv_int("CRYTON_WORKER_MAX_RETRIES", raw_settings.get("max_retries", 3))
        self.log_file = path.join(LOG_DIRECTORY, "worker.log")
        self.modules = SettingsModules(raw_settings.get("modules", {}))
        self.rabbit = SettingsRabbit(raw_settings.get("rabbit", {}))
        self.empire = SettingsEmpire(raw_settings.get("empire", {}))
        self.metasploit = SettingsMetasploit(raw_settings.get("metasploit", {}))


SETTINGS = Settings(SETTINGS_WORKER)

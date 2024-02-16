from dataclasses import dataclass
from os import getenv, sched_getaffinity, path

from cryton.lib.config.settings import (
    SETTINGS_HIVE, getenv_bool, getenv_int, getenv_list, LOG_DIRECTORY
)


@dataclass
class SettingsRabbitQueues:  # TODO: auto add a uuid to the queue name, like we do with a worker name
    attack_response: str
    agent_response: str
    event_response: str
    control_request: str

    def __init__(self, raw_settings: dict):
        self.attack_response = getenv(
            "CRYTON_HIVE_RABBIT_QUEUES_ATTACK_RESPONSE", raw_settings.get("attack_response", "cryton.attack.response")
        )
        self.agent_response = getenv(
            "CRYTON_HIVE_RABBIT_QUEUES_AGENT_RESPONSE", raw_settings.get("agent_response", "cryton.agent.response")
        )
        self.event_response = getenv(
            "CRYTON_HIVE_RABBIT_QUEUES_EVENT_RESPONSE", raw_settings.get("event_response", "cryton.event.response")
        )
        self.control_request = getenv(
            "CRYTON_HIVE_RABBIT_QUEUES_CONTROL_REQUEST", raw_settings.get("control_request", "cryton.control.response")
        )


@dataclass
class SettingsRabbit:
    host: str
    port: int
    username: str
    password: str
    queues: SettingsRabbitQueues

    def __init__(self, raw_settings: dict):
        self.host = getenv("CRYTON_HIVE_RABBIT_HOST", raw_settings.get("host", "127.0.0.1"))
        self.port = getenv_int("CRYTON_HIVE_RABBIT_PORT", raw_settings.get("port", 5672))
        self.username = getenv("CRYTON_HIVE_RABBIT_USERNAME", raw_settings.get("username", "cryton"))
        self.password = getenv("CRYTON_HIVE_RABBIT_PASSWORD", raw_settings.get("password", "cryton"))
        self.queues = SettingsRabbitQueues(raw_settings.get("queues", {}))


@dataclass
class SettingsDatabase:
    host: str
    port: int
    name: str
    username: str
    password: str

    def __init__(self, raw_settings: dict):
        self.host = getenv("CRYTON_HIVE_DATABASE_HOST", raw_settings.get("host", "127.0.0.1"))
        self.port = getenv_int("CRYTON_HIVE_DATABASE_PORT", raw_settings.get("port", 5432))
        self.name = getenv("CRYTON_HIVE_DATABASE_NAME", raw_settings.get("name", "cryton"))
        self.username = getenv("CRYTON_HIVE_DATABASE_USERNAME", raw_settings.get("username", "cryton"))
        self.password = getenv("CRYTON_HIVE_DATABASE_PASSWORD", raw_settings.get("password", "cryton"))


@dataclass
class SettingsAPI:
    secret_key: str
    allowed_hosts: list[str]
    root = "api/"

    def __init__(self, raw_settings: dict):
        self.secret_key = getenv("CRYTON_HIVE_API_SECRET_KEY", raw_settings.get("secret_key", "cryton"))
        self.allowed_hosts = getenv_list("CRYTON_HIVE_API_ALLOWED_HOSTS", raw_settings.get("allowed_hosts", "*"))


@dataclass
class SettingsScheduler:
    max_threads = 20
    max_job_instances = 1
    misfire_grace_time: int

    def __init__(self, message_timeout: int):
        self.misfire_grace_time = message_timeout + 60


@dataclass
class Settings:
    debug: bool
    message_timeout: int
    rabbit: SettingsRabbit
    database: SettingsDatabase
    api: SettingsAPI
    scheduler: SettingsScheduler
    log_file: str
    timezone = "UTC"
    threads_per_process: int
    cpu_cores: int

    def __init__(self, raw_settings: dict):
        self.debug = getenv_bool("CRYTON_HIVE_DEBUG", raw_settings.get("debug", False))
        self.message_timeout = getenv_int("CRYTON_HIVE_MESSAGE_TIMEOUT", raw_settings.get("message_timeout", 180))
        self.threads_per_process = getenv_int(
            "CRYTON_HIVE_THREADS_PER_PROCESS", raw_settings.get("threads_per_process", 7)
        )
        self.cpu_cores = getenv_int(
            "CRYTON_HIVE_CPU_CORES", raw_settings.get("cpu_cores", 3), fallback=len(sched_getaffinity(0))
        )
        self.rabbit = SettingsRabbit(raw_settings.get("rabbit", {}))
        self.database = SettingsDatabase(raw_settings.get("database", {}))
        self.api = SettingsAPI(raw_settings.get("api", {}))
        self.scheduler = SettingsScheduler(self.message_timeout)
        self.log_file = path.join(LOG_DIRECTORY, "hive.log")


SETTINGS = Settings(SETTINGS_HIVE)

# TODO: the following django settings are to be tested and removed or updated
DJANGO_STATIC_ROOT = getenv("CRYTON_CORE_API_STATIC_ROOT", "/usr/local/apache2/web/static/")
DJANGO_USE_STATIC_FILES = True if getenv("CRYTON_CORE_API_USE_STATIC_FILES", "false").lower() == "true" else False
UPLOAD_DIRECTORY_RELATIVE = "uploads/"

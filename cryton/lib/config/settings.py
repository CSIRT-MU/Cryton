from yaml import safe_load
from os import getenv, path, mkdir
from dotenv import load_dotenv


def load_config(app_directory: str) -> dict:
    config_path = path.join(app_directory, "settings.yml")
    try:
        with open(config_path) as config_file:
            return safe_load(config_file)
    except IOError:
        return {}


def getenv_bool(key: str, default: bool):
    env = getenv(key)

    return default if not env else env.lower() == "true"


def getenv_int(key: str, default: int, min_value: int = 1, fallback: int = 1):
    env = getenv(key)
    value = default if not env else int(env)

    return fallback if value < min_value else value


def getenv_list(key: str, default: list | str):
    env = getenv(key)
    value = default if not env else env

    return value.split(" ") if isinstance(value, str) else value


APP_DIRECTORY = getenv("CRYTON_APP_DIRECTORY", path.expanduser("~/.local/cryton/"))
LOGS_DIRECTORY = path.join(APP_DIRECTORY, "logs")
MODULES_DIRECTORY = path.join(APP_DIRECTORY, "modules")
EVIDENCE_DIRECTORY = path.join(APP_DIRECTORY, "evidence")

for file_path in [APP_DIRECTORY, LOGS_DIRECTORY, MODULES_DIRECTORY, EVIDENCE_DIRECTORY]:
    if not path.exists(file_path):
        mkdir(file_path)

settings = load_config(APP_DIRECTORY)
SETTINGS_CLI = settings.get("cli", {})
SETTINGS_HIVE = settings.get("hive", {})
SETTINGS_WORKER = settings.get("worker", {})

load_dotenv(path.join(APP_DIRECTORY, "settings"))

from os import getenv, sched_getaffinity, path, mkdir
from dotenv import load_dotenv


APP_DIRECTORY = getenv("CRYTON_CORE_APP_DIRECTORY", path.expanduser("~/.local/cryton-core/"))

load_dotenv(path.join(APP_DIRECTORY, ".env"))

REPORT_DIRECTORY = path.join(APP_DIRECTORY, "reports/")
EVIDENCE_DIRECTORY = path.join(APP_DIRECTORY, "evidence/")
LOG_DIRECTORY = path.join(APP_DIRECTORY, "log/")

for file_path in [APP_DIRECTORY, REPORT_DIRECTORY, EVIDENCE_DIRECTORY, LOG_DIRECTORY]:
    if not path.exists(file_path):
        mkdir(file_path)

LOG_FILE_PATH = path.join(LOG_DIRECTORY, "cryton-core.log")
LOG_FILE_PATH_DEBUG = path.join(LOG_DIRECTORY, "cryton-core-debug.log")

TIME_ZONE = "UTC"

DEBUG = True if getenv("CRYTON_CORE_DEBUG", "false").lower() == "true" else False

DB_NAME = getenv("CRYTON_CORE_DB_NAME", "cryton")
DB_USERNAME = getenv("CRYTON_CORE_DB_USERNAME", "cryton")
DB_PASSWORD = getenv("CRYTON_CORE_DB_PASSWORD", "cryton")
DB_HOST = getenv("CRYTON_CORE_DB_HOST", "127.0.0.1")
DB_PORT = int(getenv("CRYTON_CORE_DB_PORT", 5432))

RABBIT_USERNAME = getenv("CRYTON_CORE_RABBIT_USERNAME", "cryton")
RABBIT_PASSWORD = getenv("CRYTON_CORE_RABBIT_PASSWORD", "cryton")
RABBIT_HOST = getenv("CRYTON_CORE_RABBIT_HOST", "127.0.0.1")
RABBIT_PORT = int(getenv("CRYTON_CORE_RABBIT_PORT", 5672))

Q_ATTACK_RESPONSE_NAME = getenv("CRYTON_CORE_Q_ATTACK_RESPONSE", "cryton_core.attack.response")
Q_AGENT_RESPONSE_NAME = getenv("CRYTON_CORE_Q_AGENT_RESPONSE", "cryton_core.agent.response")
Q_EVENT_RESPONSE_NAME = getenv("CRYTON_CORE_Q_EVENT_RESPONSE", "cryton_core.event.response")
Q_CONTROL_REQUEST_NAME = getenv("CRYTON_CORE_Q_CONTROL_REQUEST", "cryton_core.control.request")

# available cores to the application
CPU_CORES = int(getenv("CRYTON_CORE_CPU_CORES", 3))
if CPU_CORES == 0:
    CPU_CORES = len(sched_getaffinity(0))
EXECUTION_THREADS_PER_PROCESS = int(getenv("CRYTON_CORE_EXECUTION_THREADS_PER_PROCESS", 7))

MESSAGE_TIMEOUT = int(getenv("CRYTON_CORE_MESSAGE_TIMEOUT", 180))

DJANGO_API_ROOT_URL = "api/"
DJANGO_ALLOWED_HOSTS = getenv("CRYTON_CORE_API_ALLOWED_HOSTS", "*").split(" ")
DJANGO_STATIC_ROOT = getenv("CRYTON_CORE_API_STATIC_ROOT", "/usr/local/apache2/web/static/")
DJANGO_SECRET_KEY = getenv("CRYTON_CORE_API_SECRET_KEY", "cryton")
DJANGO_USE_STATIC_FILES = True if getenv("CRYTON_CORE_API_USE_STATIC_FILES", "false").lower() == "true" else False
UPLOAD_DIRECTORY_RELATIVE = "uploads/"

SCHEDULER_MAX_THREADS = 20
SCHEDULER_MAX_JOB_INSTANCES = 1
SCHEDULER_MISFIRE_GRACE_TIME = MESSAGE_TIMEOUT + 60

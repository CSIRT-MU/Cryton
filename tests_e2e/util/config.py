from os import getenv, path
from pathlib import Path

ROOT_DIRECTORY = Path(__file__).parent.parent.parent.absolute()

# RESOURCES_DIRECTORY = path.join(ROOT_DIRECTORY, "examples/scenarios")
TEMPLATES_DIRECTORY = path.join(ROOT_DIRECTORY, "examples/scenarios")
E2E_DIRECTORY = path.join(ROOT_DIRECTORY, "tests_e2e")
CRYTON_CLI_EXECUTABLE = getenv("CRYTON_E2E_CLI_EXECUTABLE", "cryton-cli")
WORKER_ADDRESS = getenv("CRYTON_E2E_WORKER_ADDRESS", "127.0.0.1")
WORKER_NAME = getenv("CRYTON_E2E_WORKER_NAME", "worker")

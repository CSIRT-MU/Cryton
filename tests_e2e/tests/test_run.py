import time
import click
from typing import List, Dict, Optional

from tests_e2e.tests.test import Test
from tests_e2e.util.exceptions import CannotParseResponseError, TimeOutError, UnexpectedResponse


class TestRun(Test):
    """
    Base class for Run testing.
    """

    def __init__(
        self,
        template: str,
        workers: List[Dict],
        inventories: Optional[List[str]],
        execution_variables: Optional[List[str]],
        max_timeout: int,
    ):
        super().__init__()
        self.max_timeout = max_timeout

        self.template = template
        self.inventories = inventories
        self.workers = workers
        self.execution_variables = execution_variables

        self.template_id = None
        self.plan_id = None
        self.worker_ids = []
        self.run_id = None
        self.plan_execution_ids = []
        self.execution_variable_ids = []
        self.results = {}

    def _prepare(self):
        """
        Prepares everything in order to start the actual test(s).
        :return: None
        """
        click.echo("Preparing Workers... ", nl=False)
        self._prepare_workers()
        click.secho("OK", fg="green")

        click.echo("Preparing template... ", nl=False)
        self._prepare_template()
        click.secho("OK", fg="green")

        click.echo("Preparing Plan... ", nl=False)
        self._prepare_plan()
        click.secho("OK", fg="green")

        click.echo("Preparing Run... ", nl=False)
        self._prepare_run()
        click.secho("OK", fg="green")

        if self.execution_variables is not None:
            click.echo("Preparing execution variables... ", nl=False)
            self._prepare_execution_variables()
            click.secho("OK", fg="green")

    def _prepare_workers(self):
        """
        Prepares Workers.
        :return: None
        """
        for worker in self.workers:
            worker_name, worker_description = worker.get("name"), worker.get("description")
            cmd = ["workers", "create", worker_name, "-d", worker_description]

            result = self._cli_call_json(cmd)
            if "already exists" in str(result):
                cmd = ["workers", "list", "-f", "name", worker_name]
                result = self._cli_call_json(cmd)

                try:
                    self.worker_ids.append(result["results"][0]["id"])
                except (ValueError, KeyError):
                    raise CannotParseResponseError(f"Couldn't get Worker. Original result: {result}")
            else:
                try:
                    self.worker_ids.append(result["id"])
                except (ValueError, KeyError):
                    raise CannotParseResponseError(f"Couldn't create Worker. Original result: {result}")

    def _prepare_template(self):
        """
        Prepares template.
        :return: None
        """
        cmd = ["plan-templates", "create", self.template]
        result = self._cli_call_json(cmd)

        try:
            self.template_id = result.get("id")
        except (ValueError, KeyError):
            raise CannotParseResponseError(f"Couldn't create template. Original result: {result}")

    def _prepare_plan(self):
        """
        Prepares Plan.
        :return: None
        """
        cmd = ["plans", "create", str(self.template_id)]
        if self.inventories is not None and len(self.inventories) != 0:
            for inventory_file in self.inventories:
                cmd.extend(["-i", inventory_file])
        result = self._cli_call_json(cmd)

        try:
            self.plan_id = result["id"]
        except (ValueError, KeyError):
            raise CannotParseResponseError(f"Couldn't create Plan. Original result: {result}")

    def _prepare_run(self):
        """
        Prepares Run.
        :return: None
        """
        cmd = ["runs", "create", str(self.plan_id)]
        cmd.extend(map(str, self.worker_ids))
        result = self._cli_call_json(cmd)

        try:
            self.run_id = result["id"]
            self.plan_execution_ids = result["plan_execution_ids"]
        except (ValueError, KeyError):
            raise CannotParseResponseError(f"Couldn't create Run. Original result: {result}")

    def _prepare_execution_variables(self):
        """
        Prepares execution variables.
        :return: None
        """
        if self.execution_variables is None or len(self.execution_variables) == 0:
            return

        for plan_execution_id in self.plan_execution_ids:
            cmd = ["execution-variables", "create", str(plan_execution_id)]
            cmd.extend([execution_variable_file for execution_variable_file in self.execution_variables])
            result = self._cli_call_json(cmd)

            try:
                self.execution_variable_ids.extend(result["ids"])
            except (ValueError, KeyError):
                raise CannotParseResponseError(f"Couldn't prepare. Original result: {result}")

    def get_pre_info(self) -> Dict:
        """
        Gets pre-test information.
        :return: Information that will be printed to the user
        """
        return {
            "CLI executable": self._executable,
            "template_id": self.template_id,
            "plan_id": self.plan_id,
            "worker_ids": ", ".join(map(str, self.worker_ids)),
            "run_id": self.run_id,
            "plan_execution_ids": ", ".join(map(str, self.plan_execution_ids)),
            "execution_variable_ids": ", ".join(map(str, self.execution_variable_ids)),
        }

    def run_wait_for_state(self, state: str, timeout: int):
        """
        Waits for the correct state (of Run) desired by the user.
        :param state: Desired state
        :param timeout: When to stop
        :return: None
        """
        click.echo(f"Waiting for Run's state change to {state}... ", nl=False)
        cmd = ["runs", "show", str(self.run_id)]
        for i in range(timeout):
            time.sleep(1)
            result = self._cli_call_json(cmd)
            try:
                current_state = result["state"]
            except (ValueError, KeyError):
                raise CannotParseResponseError(f"Couldn't get the state. Original result: {result}")

            if current_state == state:
                click.secho("OK", fg="green")
                return

        raise TimeOutError(f"State change timeout after {timeout} seconds.")

    @staticmethod
    def check_result(result: str, check_word: str):
        """
        Check if a phrase is present in a result.
        :param result: Result to check
        :param check_word: Phrase to check
        :return: None
        """
        if check_word not in result.lower():
            raise UnexpectedResponse(f"Got an unexpected response. Original result: {result}")
        parsed_result = result.replace("\n", "")
        click.echo(f"{click.style('OK', 'green')} - {parsed_result}")

    def test(self, test_info: str, cmd: List, check_word: str, state: str = None, timeout: int = None):
        """
        Run a test, optionally wait for a Run's state change.
        :param test_info: Test's purpose
        :param cmd: Command to execute
        :param check_word: Phrase to check
        :param state: Desired state to wait for
        :param timeout: Time to wait for the desired state
        :return: None
        """
        click.echo(f"{test_info}... ", nl=False)
        result = self._cli_call(cmd)
        self.check_result(result, check_word)

        if state is not None:  # this works only with Run!
            timeout = timeout if timeout is not None else self.max_timeout
            self.run_wait_for_state(state, timeout)

    def get_step_results(self):
        """
        Get Step executions' results and check if they finished in `OK`.
        :return: None
        """
        cmd = ["runs", "report", str(self.run_id)]
        json_report = self._cli_call_json(cmd)

        failed_steps = []
        for plan_exs in json_report["detail"]["plan_executions"]:
            for stage_exs in plan_exs["stage_executions"]:
                for step in stage_exs["step_executions"]:
                    if step["result"] != "ok":
                        failed_steps.append(step["name"])

        if failed_steps:
            self.results["failed_steps"] = failed_steps

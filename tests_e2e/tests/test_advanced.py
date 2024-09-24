from typing import List, Dict, Optional

from tests_e2e.tests import TestRunExecution, TestRunControl
from tests_e2e.util import helpers


class TestAdvancedExecution(TestRunExecution):
    """
    Advanced Run execution testing.
    """

    def __init__(
        self,
        template: str,
        workers: List[Dict],
        inventories: Optional[List[str]],
        execution_variables: Optional[List[str]],
        max_timeout: int,
    ):
        super().__init__(template, workers, inventories, execution_variables, max_timeout)
        self.description = f"Advanced test: {self.description}"

    def _run_tests(self):
        """
        Runs the tests.
        :return: None
        """
        # Execute Run
        self.test("Executing Run", ["runs", "execute", str(self.run_id)], "executed", "RUNNING", 5)

        # Trigger the HTTP listener
        helpers.trigger_http_listener()

        # Trigger the MSF listener
        helpers.trigger_msf_listener()

        # Wait for the correct Run's state
        self.run_wait_for_state("FINISHED", 30)

        # Get Run report
        self.test("Getting Run's report", ["runs", "report", str(self.run_id), "--localize"], "detail")


class TestAdvancedControl(TestRunControl):
    """
    Advanced Run control testing.
    """

    def __init__(
        self,
        template: str,
        workers: List[Dict],
        inventories: Optional[List[str]],
        execution_variables: Optional[List[str]],
        max_timeout: int,
    ):
        super().__init__(template, workers, inventories, execution_variables, max_timeout)
        self.description = f"Advanced test: {self.description}"

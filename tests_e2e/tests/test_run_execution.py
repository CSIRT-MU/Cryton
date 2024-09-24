from typing import List, Dict, Optional

from tests_e2e.tests.test_run import TestRun


class TestRunExecution(TestRun):
    """
    Base class for Run execution testing.
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
        self.description = "Setup and execute a Run."

    def _run_tests(self):
        """
        Runs the tests.
        :return: None
        """
        # Execute Run
        self.test("Executing Run", ["runs", "execute", str(self.run_id)], "executed", "FINISHED")

        # Get Run report
        self.test("Getting Run's report", ["runs", "report", str(self.run_id), "--localize"], "detail")

        # Check if any steps failed
        self.get_step_results()

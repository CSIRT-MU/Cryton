from typing import List, Dict, Optional

from tests_e2e.tests.test_run import TestRun


class TestRunControl(TestRun):
    """
    Base class for Run control testing.
    """
    def __init__(self, template: str, workers: List[Dict], inventories: Optional[List[str]],
                 execution_variables: Optional[List[str]], max_timeout: int):
        super().__init__(template, workers, inventories, execution_variables, max_timeout)
        self.description = "Call all commands used for executing a Run"

    def _run_tests(self):
        """
        Runs the tests.
        :return: None
        """
        # Show Run
        self.test("Show Run information", ["runs", "show", str(self.run_id)], f'"id":{self.run_id}')

        # Validate modules in Run
        self.test("Validating modules in Run", ["runs", "validate-modules", str(self.run_id)], "were validated")

        # Get Run's Plan
        self.test("Getting Run's Plan", ["runs", "get-plan", str(self.run_id)], "detail")

        # Schedule Run
        self.test("Scheduling Run", ["runs", "schedule", str(self.run_id), "2050-01-01", "20:00:00"], "scheduled",
                  "SCHEDULED", 5)

        # Reschedule Run
        self.test("Rescheduling Run", ["runs", "reschedule", str(self.run_id), "2050-01-01", "21:00:00"], "rescheduled",
                  "SCHEDULED", 5)

        # Postpone Run
        self.test("Postponing Run", ["runs", "postpone", str(self.run_id), "1:1:1"], "postponed", "SCHEDULED", 5)

        # Unschedule Run
        self.test("Unscheduling Run", ["runs", "unschedule", str(self.run_id)], "unscheduled", "PENDING", 5)

        # Execute Run
        self.test("Executing Run", ["runs", "execute", str(self.run_id)], "executed", "RUNNING", 5)

        # Pause Run
        self.test("Pausing Run", ["runs", "pause", str(self.run_id)], "paused", "PAUSED", 10)

        # Resume Run
        self.test("Resuming Run", ["runs", "resume", str(self.run_id)], "resumed", "RUNNING", 5)

        # Kill Run
        self.test("Terminating Run", ["runs", "kill", str(self.run_id)], "terminated", "TERMINATED", 5)

        # Get Run report
        self.test("Getting Run's report", ["runs", "report", str(self.run_id), "--localize"], "detail")

        # Delete Run
        self.test("Deleting Run", ["runs", "delete", str(self.run_id)], "")

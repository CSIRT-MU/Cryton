from typing import List, Dict, Optional

from tests_e2e.tests import TestRunExecution


class TestEmpireExecution(TestRunExecution):
    """
    Empire Run execution testing.
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
        self.description = f"Empire test: {self.description}"

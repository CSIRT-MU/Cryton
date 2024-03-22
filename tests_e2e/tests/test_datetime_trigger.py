import datetime
from typing import List, Dict, Optional
import yaml

from tests_e2e.tests import TestRunExecution
from tests_e2e.util import helpers


class TestDatetimeTriggerExecution(TestRunExecution):
    """
    Datetime trigger Run execution testing.
    """
    def __init__(self, template: str, workers: List[Dict], inventories: Optional[List[str]],
                 execution_variables: Optional[List[str]], max_timeout: int):
        start_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
        with open(template) as f:
            loaded_template: dict = yaml.safe_load(f)
        loaded_template["plan"]["stages"][0]["trigger_args"] = {
            "timezone": "UTC", "hour": start_time.hour, "minute": start_time.minute, "second": start_time.second
        }
        updated_template = helpers.create_inventory(loaded_template)

        super().__init__(updated_template, workers, inventories, execution_variables, max_timeout)
        self.description = f"DateTime trigger test: {self.description}"

from threading import Thread

from cryton.hive.utility import states, logger
from cryton.hive.triggers.trigger_base import TriggerBase


class TriggerImmediate(TriggerBase):
    def start(self) -> None:
        """
        Start the trigger.
        :return: None
        """
        Thread(target=self.stage_execution.execute).start()

    def pause(self) -> None:
        """
        Pause stage execution.
        :return: None
        """
        # If stage is RUNNING, set PAUSING state. It will be PAUSED once the currently
        # RUNNING step finished and listener gets it's return value
        if self.stage_execution.state == states.RUNNING:
            logger.logger.info("Stage execution pausing", stage_execution_id=self.stage_execution_id)
            self.stage_execution.state = states.PAUSING

from threading import Thread
from datetime import datetime, timedelta
from django.utils import timezone
import schema

from cryton.hive.triggers.trigger_base import TriggerTime


class TriggerDelta(TriggerTime):
    arg_schema = schema.Schema({schema.Or("hours", "minutes", "seconds", only_one=False): int})

    def __init__(self, stage_execution):
        """
        :param stage_execution: StageExecution's object
        """
        super().__init__(stage_execution)

    def start(self):
        """
        Start the trigger.
        :return: None
        """
        if self._get_delta().total_seconds() < 1:
            Thread(target=self.stage_execution.execute).start()
        else:
            self.schedule()

    def _get_delta(self) -> timedelta:
        """
        Calculate the delta used for postponing.
        :return: Time delta
        """
        trigger_args = self.stage_execution.model.stage_model.trigger_args
        delta = timedelta(
            hours=trigger_args.get("hours", 0),
            minutes=trigger_args.get("minutes", 0),
            seconds=trigger_args.get("seconds", 0),
        )

        if self.stage_execution.pause_time:
            return self.stage_execution.model.plan_execution.start_time + delta - self.stage_execution.pause_time
        return delta

    def _create_schedule_time(self) -> datetime:
        """
        Create Stage's supposed start time.
        :return: Stage's supposed start time
        """
        return timezone.now() + self._get_delta()

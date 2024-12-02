from datetime import datetime, timedelta
from django.utils import timezone

from cryton.hive.triggers.abstract import Trigger
from cryton.hive.utility import scheduler_client


class TriggerDelta(Trigger):
    @classmethod
    def start(cls, **kwargs) -> tuple[str, datetime | None]:
        schedule_time = cls._create_schedule_time(kwargs["arguments"], kwargs.get("new_start_time"))
        trigger_id = scheduler_client.schedule_function(
            "cryton.hive.models.stage:execution", [kwargs["stage_execution_id"]], schedule_time
        )

        return trigger_id, schedule_time

    @classmethod
    def stop(cls, **kwargs) -> None:
        scheduler_client.remove_job(kwargs["trigger_id"])

    @staticmethod
    def _create_schedule_time(arguments: dict, new_start_time: datetime | None) -> datetime:
        """
        Create Stage's supposed start time.
        :return: Stage's supposed start time
        """
        delta = timedelta(
            hours=arguments.get("hours", 0), minutes=arguments.get("minutes", 0), seconds=arguments.get("seconds", 0)
        )

        if new_start_time:
            return new_start_time + delta

        return timezone.now() + delta

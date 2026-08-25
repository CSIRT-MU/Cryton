from datetime import datetime
import pytz

from cryton.hive.utility import util, scheduler_client
from cryton.hive.triggers.abstract import Trigger


class TriggerTime(Trigger):
    """
    Time trigger.
    """

    @classmethod
    def start(cls, **kwargs) -> tuple[str, datetime | None]:
        schedule_time = cls._create_schedule_time(kwargs["arguments"])
        trigger_id = scheduler_client.schedule_function(
            "cryton.hive.models.stage:execution", [kwargs["stage_execution_id"]], schedule_time
        )

        return trigger_id, schedule_time

    @classmethod
    def stop(cls, **kwargs) -> None:
        scheduler_client.remove_job(kwargs["trigger_id"])

    @staticmethod
    def _create_schedule_time(arguments: dict) -> datetime:
        """
        Create Stage's start time.
        :return: Stage's start time
        """
        timezone = arguments.get("timezone", "UTC")
        current_time = datetime.now(pytz.timezone(timezone))

        schedule_datetime = datetime(
            year=arguments.get("year", current_time.year),
            month=arguments.get("month", current_time.month),
            day=arguments.get("day", current_time.day),
            hour=arguments.get("hour", 0),
            minute=arguments.get("minute", 0),
            second=arguments.get("second", 0),
        )

        if schedule_datetime.tzinfo != pytz.utc:
            schedule_datetime = util.convert_to_utc(schedule_datetime, timezone)

        return schedule_datetime

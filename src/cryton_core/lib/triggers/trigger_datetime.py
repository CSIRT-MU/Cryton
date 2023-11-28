from datetime import datetime
from schema import Schema, Optional, Or
import pytz
from threading import Thread

from cryton_core.lib.util import util
from cryton_core.lib.triggers.trigger_base import TriggerTime


class TriggerDateTime(TriggerTime):
    arg_schema = Schema({
        Or('year', 'month', 'day', 'hour', 'minute', 'second', only_one=False): int,
        # validates that the supplied timezone is in pytz timezones
        Optional('timezone'): Or(lambda x: x in pytz.all_timezones, None, error='Invalid timezone')
        })

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
        if (self._create_schedule_time() - datetime.utcnow()).total_seconds() < 1:
            Thread(target=self.stage_execution.execute).start()
        else:
            self.schedule()

    def _create_schedule_time(self) -> datetime:
        """
        Create Stage's start time.
        :return: Stage's start time
        """
        trigger_args = self.stage_execution.model.stage_model.trigger_args
        timezone = trigger_args.get('timezone', 'UTC')

        today = datetime.now(pytz.timezone(timezone))

        schedule_datetime = datetime(year=trigger_args.get('year', today.year),
                                     month=trigger_args.get('month', today.month),
                                     day=trigger_args.get('day', today.day), hour=trigger_args.get('hour', 0),
                                     minute=trigger_args.get('minute', 0), second=trigger_args.get('second', 0))

        if schedule_datetime.tzinfo != pytz.utc:
            schedule_datetime = util.convert_to_utc(schedule_datetime, timezone)

        return schedule_datetime

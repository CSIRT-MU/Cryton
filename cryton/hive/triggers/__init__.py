from enum import Enum, EnumMeta

from cryton.hive.utility.exceptions import TriggerTypeDoesNotExist
from cryton.hive.triggers.trigger_delta import TriggerDelta
from cryton.hive.triggers.trigger_http import TriggerHTTP
from cryton.hive.triggers.trigger_msf import TriggerMSF
from cryton.hive.triggers.trigger_datetime import TriggerDateTime


class TriggerTypeMeta(EnumMeta):
    """
    Overrides base metaclass of Enum in order to support custom exception when accessing not present item.
    """
    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            raise TriggerTypeDoesNotExist(item, [trigger.name for trigger in list(self)])


class TriggerType(Enum, metaclass=TriggerTypeMeta):
    delta = TriggerDelta
    HTTPListener = TriggerHTTP
    MSFListener = TriggerMSF
    datetime = TriggerDateTime

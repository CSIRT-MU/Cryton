from enum import Enum, EnumMeta

from cryton.worker.utility import exceptions, constants
from cryton.worker.triggers.listener_base import Listener
from cryton.worker.triggers.listener_http import HTTPListener
from cryton.worker.triggers.listener_msf import MSFListener


class ListenerTypeMeta(EnumMeta):
    """
    Overrides base metaclass of Enum in order to support custom exception when accessing not present item.
    """
    def __getitem__(self, item):
        try:
            return super().__getitem__(item).value
        except KeyError:
            raise exceptions.ListenerTypeDoesNotExist(item, [listener.name for listener in list(self)])


class ListenerEnum(Enum, metaclass=ListenerTypeMeta):
    """
    Keys according to lib.util.constants
    """
    HTTP = HTTPListener
    MSF = MSFListener


class ListenerIdentifiersEnum(Enum, metaclass=ListenerTypeMeta):
    """
    Keys according to lib.util.constants
    """
    HTTP = [constants.LISTENER_PORT, constants.LISTENER_HOST]
    MSF = [constants.IDENTIFIERS]

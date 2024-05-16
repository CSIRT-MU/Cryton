from schema import Schema, Optional, Or

from cryton.hive.triggers.trigger_base import TriggerWorker
from cryton.hive.utility import constants
from cryton.hive.config.settings import SETTINGS
from cryton.modules.metasploit.module import Module as MetasploitModule


class TriggerMSF(TriggerWorker):
    SCHEMA = MetasploitModule.SCHEMA
    arg_schema = Schema({})  # TODO: remove once we remove schema

    def __init__(self, stage_execution):
        """
        :param stage_execution: StageExecution's object
        """
        super().__init__(stage_execution)

    def start(self) -> None:
        """
        Start MSF listener.
        :return: None
        """
        event_v = {constants.TRIGGER_TYPE: "MSF", constants.REPLY_TO: SETTINGS.rabbit.queues.event_response}
        self._rpc_start(event_v)

    def stop(self) -> None:
        """
        Stop MSF listener.
        :return: None
        """
        self._rpc_stop()

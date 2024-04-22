import schema

from cryton.hive.triggers.trigger_base import TriggerWorker
from cryton.hive.utility import constants
from cryton.hive.config.settings import SETTINGS


class TriggerHTTP(TriggerWorker):
    arg_schema = schema.Schema(
        {
            "host": str,
            "port": int,
            "routes": [{"path": str, "method": str, "parameters": [{"name": str, "value": str}]}],
        }
    )

    def __init__(self, stage_execution):
        """
        :param stage_execution: StageExecution's object
        """
        super().__init__(stage_execution)

    def start(self) -> None:
        """
        Start HTTP listener.
        :return: None
        """
        event_v = {constants.TRIGGER_TYPE: "HTTP", constants.REPLY_TO: SETTINGS.rabbit.queues.event_response}
        self._rpc_start(event_v)

    def stop(self) -> None:
        """
        Stop HTTP listener.
        :return: None
        """
        self._rpc_stop()

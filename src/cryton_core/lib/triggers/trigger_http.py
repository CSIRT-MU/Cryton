import schema

from cryton_core.lib.triggers.trigger_base import TriggerWorker
from cryton_core.lib.util import constants
from cryton_core.etc import config


class TriggerHTTP(TriggerWorker):
    arg_schema = schema.Schema({
        'host': str,
        'port': int,
        'routes': [
            {
                'path': str,
                'method': str,
                'parameters': [
                    {
                        'name': str,
                        'value': str
                    }
                ]
            }
        ]
    })

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
        event_v = {constants.TRIGGER_TYPE: "HTTP", constants.REPLY_TO: config.Q_EVENT_RESPONSE_NAME}
        self._rpc_start(event_v)

    def stop(self) -> None:
        """
        Stop HTTP listener.
        :return: None
        """
        self._rpc_stop()

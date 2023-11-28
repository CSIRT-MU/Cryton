from schema import Schema, Optional, Or

from cryton_core.lib.triggers.trigger_base import TriggerWorker
from cryton_core.lib.util import constants
from cryton_core.etc import config


class TriggerMSF(TriggerWorker):
    arg_schema = Schema(Or(
        {
            Optional('identifiers'): {
                Or('type', 'tunnel_local', 'tunnel_peer', 'via_exploit', 'via_payload', 'desc', 'info', 'workspace',
                   'session_host', 'session_port', 'target_host', 'username', 'uuid', 'exploit_uuid', 'routes', 'arch',
                   only_one=False): Or(str, int, bool)
            },
            'exploit': str,
            'payload': str,
            Optional("exploit_arguments"): {
                Optional(str): Or(str, int, bool)
            },
            Optional("payload_arguments"): {
                Optional(str): Or(str, int, bool)
            }
        },
        {
            Optional('identifiers'): {
                Or('type', 'tunnel_local', 'tunnel_peer', 'via_exploit', 'via_payload', 'desc', 'info', 'workspace',
                   'session_host', 'session_port', 'target_host', 'username', 'uuid', 'exploit_uuid', 'routes', 'arch',
                   only_one=False): Or(str, int, bool)
            },
            'auxiliary': str,
            Optional("auxiliary_arguments"): {
                Optional(str): Or(str, int, bool)
            }
        }
    ))

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
        event_v = {constants.TRIGGER_TYPE: "MSF", constants.REPLY_TO: config.Q_EVENT_RESPONSE_NAME}
        self._rpc_start(event_v)

    def stop(self) -> None:
        """
        Stop MSF listener.
        :return: None
        """
        self._rpc_stop()

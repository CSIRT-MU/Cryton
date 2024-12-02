from datetime import datetime

from cryton.hive.utility import constants
from cryton.hive.config.settings import SETTINGS
from cryton.hive.triggers.abstract import Trigger
from cryton.hive.models.worker import Worker
from cryton.hive.utility.rabbit_client import RpcClient
from cryton.lib.utility.module import Result


class TriggerMetasploit(Trigger):
    @classmethod
    def start(cls, **kwargs) -> tuple[str, datetime | None]:
        event_v = {constants.TRIGGER_TYPE: "MSF", constants.REPLY_TO: SETTINGS.rabbit.queues.event_response} | kwargs[
            "arguments"
        ]
        message = {constants.EVENT_T: constants.EVENT_ADD_TRIGGER, constants.EVENT_V: event_v}

        with RpcClient() as rpc:
            response = rpc.call(kwargs["queue"], message)
        if response.get(constants.EVENT_V).get(constants.RESULT) != Result.OK:
            raise Exception("Unable to start the trigger")

        return response.get(constants.EVENT_V).get(constants.TRIGGER_ID), None

    @classmethod
    def stop(cls, **kwargs) -> None:
        message = {
            constants.EVENT_T: constants.EVENT_REMOVE_TRIGGER,
            constants.EVENT_V: {constants.TRIGGER_ID: kwargs["trigger_id"]},
        }

        with RpcClient() as rpc:
            response = rpc.call(kwargs["queue"], message)
        if response.get(constants.EVENT_V).get(constants.RESULT) != Result.OK:
            raise Exception("Unable to stop the trigger")

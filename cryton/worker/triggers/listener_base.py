from click import echo
from threading import Lock
from queue import PriorityQueue

from cryton.worker.utility import logger, constants as co, util


class Listener:
    def __init__(self, main_queue: PriorityQueue):
        """
        Base class for Triggers.
        :param main_queue: Worker's queue for internal request processing
        """
        self._main_queue = main_queue
        self._triggers: list[dict] = []
        self._identifiers: dict = {}
        self._triggers_lock = Lock()  # Lock to prevent modifying, while performing time-consuming actions.
        self._logger = logger.logger.bind()

    def compare_identifiers(self, identifiers: dict) -> bool:
        """
        Check if specified identifiers match with Listener or its triggers.
        :param identifiers: Data containing identifiers
        :return: True if identifiers match Listener's
        """
        pass

    def find_trigger(self, trigger_id: str) -> dict | None:
        """
        Match and return trigger using its ID.
        :param trigger_id: Trigger's ID
        :return: Trigger if found, else None
        """
        with self._triggers_lock:
            for trigger in self._triggers:
                if trigger.get(co.TRIGGER_ID) == trigger_id:
                    return trigger
        return None

    def start(self) -> None:
        """
        Start the Listener.
        :return: None
        """
        pass

    def stop(self) -> None:
        """
        Stop the Listener.
        :return: None
        """
        pass

    def add_trigger(self, details: dict) -> None:
        """
        Add trigger.
        :param details: Trigger options
        :return: None
        """
        pass

    def remove_trigger(self, details: dict) -> None:
        """
        Remove trigger.
        :param details: Trigger options
        :return: None
        """
        pass

    def get_triggers(self) -> list[dict]:
        """
        Get list of all triggers.
        :return: Listener's triggers
        """
        with self._triggers_lock:
            return self._triggers

    def any_trigger_exists(self) -> bool:
        """
        Check if Listener triggers are empty.
        :return: True if Listener has no triggers
        """
        return False if len(self._triggers) == 0 else True

    def _notify(self, queue_name: str, message_body: dict) -> None:
        """
        Send message to reply_to about successful trigger call.
        :param queue_name: Target queue (message receiver)
        :param message_body: Message content
        :return: None
        """
        echo(
            f"Notifying about successful trigger call. trigger_type: {self.__class__}, "
            f"identifiers: {self._identifiers}"
        )
        self._logger.debug("notifying about successful trigger call", trigger_type=self.__class__)
        item = util.PrioritizedItem(
            co.HIGH_PRIORITY,
            {co.ACTION: co.ACTION_SEND_MESSAGE, co.QUEUE_NAME: queue_name, co.DATA: message_body, co.PROPERTIES: {}},
        )
        self._main_queue.put(item)

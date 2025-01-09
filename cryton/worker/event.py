from multiprocessing import Pipe
from queue import PriorityQueue
from dataclasses import asdict

from cryton.worker.utility import util, constants as co, logger


class Event:
    def __init__(self, event_details: dict, main_queue: PriorityQueue):
        """
        Class for processing events.
        :param event_details: Received event details
        :param main_queue: Worker's queue for internal request processing
        """
        self._logger = logger.logger.bind(event_details=event_details)
        self._event_details = event_details
        self._main_queue = main_queue
        self._response_pipe, self._request_pipe = Pipe(False)

    def validate_module(self) -> dict:
        """
        Validate requested module.
        :return: Details about the event result
        """
        self._logger.debug("running event: validate_module")
        attack_module = self._event_details.get(co.MODULE)
        module_arguments = self._event_details.get(co.ARGUMENTS)
        return asdict(util.run_module(attack_module, module_arguments, validate_only=True))

    def stop_step_execution(self) -> dict:
        """
        Stop Step's Execution (AttackTask) using correlation ID.
        :return: Details about the event result
        """
        self._logger.debug("running event: stop_step_execution")
        correlation_id = self._event_details.get(co.CORRELATION_ID)
        item = util.PrioritizedItem(
            co.MEDIUM_PRIORITY,
            {co.ACTION: co.ACTION_STOP_TASK, co.RESULT_PIPE: self._request_pipe, co.CORRELATION_ID: correlation_id},
        )
        self._main_queue.put(item)
        return self._response_pipe.recv()

    def health_check(self) -> dict:
        """
        Check if Worker is UP and running.
        :return: Details about the event result
        """
        self._logger.debug("running event: health_check")
        result = co.CODE_OK
        return {co.RESULT: result}

    def add_trigger(self) -> dict:
        """
        Add Trigger.
        :return: Details about the event result
        """
        self._logger.debug("running event: add_trigger")
        item = util.PrioritizedItem(
            co.MEDIUM_PRIORITY,
            {co.ACTION: co.ACTION_ADD_TRIGGER, co.RESULT_PIPE: self._request_pipe, co.DATA: self._event_details},
        )
        self._main_queue.put(item)
        return self._response_pipe.recv()

    def remove_trigger(self) -> dict:
        """
        Remove trigger.
        :return: Details about the event result
        """
        self._logger.debug("running event: remove_trigger")
        item = util.PrioritizedItem(
            co.MEDIUM_PRIORITY,
            {co.ACTION: co.ACTION_REMOVE_TRIGGER, co.RESULT_PIPE: self._request_pipe, co.DATA: self._event_details},
        )
        self._main_queue.put(item)
        return self._response_pipe.recv()

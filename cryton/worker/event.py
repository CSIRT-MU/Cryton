from multiprocessing import Pipe
from queue import PriorityQueue
from dataclasses import asdict

from cryton.worker.utility import util, constants as co, logger
from cryton.lib.metasploit import MetasploitClientUpdated
from snek_sploit import Error as MSFError, SessionInformation


class Event:
    def __init__(self, event_details: dict, main_queue: PriorityQueue):
        """
        Class for processing events.
        :param event_details: Received event details
        :param main_queue: Worker's queue for internal request processing
        """
        self._event_details = event_details
        self._main_queue = main_queue
        self._response_pipe, self._request_pipe = Pipe(False)

    def validate_module(self) -> dict:
        """
        Validate requested module.
        :return: Details about the event result
        """
        logger.logger.debug("Running event: validate_module", event_details=self._event_details)
        attack_module = self._event_details.get(co.MODULE)
        module_arguments = self._event_details.get(co.MODULE_ARGUMENTS)
        return asdict(util.run_module(attack_module, module_arguments, validate_only=True))

    def list_modules(self) -> dict:
        """
        List all modules available on Worker.
        :return: Details about the event result
        """
        logger.logger.debug("Running event: list_modules", event_details=self._event_details)
        result = [module_path.removeprefix("cryton.modules.") for module_path in util.get_available_modules().keys()]
        return {co.MODULE_LIST: result}

    def list_sessions(self) -> dict:
        """
        List all sessions available on Worker and filter them using event_details.
        :return: Details about the event result
        """
        logger.logger.debug("Running event: list_sessions", event_details=self._event_details)
        options = self._event_details
        try:
            msf = MetasploitClientUpdated()
            sessions = msf.sessions.filter(SessionInformation(**options))
            return {co.SESSION_LIST: list(sessions.keys())}
        except MSFError as ex:
            return {co.SESSION_LIST: [], co.OUTPUT: str(ex)}

    def kill_step_execution(self) -> dict:
        """
        Kill Step's Execution (AttackTask) using correlation ID.
        :return: Details about the event result
        """
        logger.logger.debug("Running event: kill_step_execution", event_details=self._event_details)
        correlation_id = self._event_details.get(co.CORRELATION_ID)
        item = util.PrioritizedItem(
            co.MEDIUM_PRIORITY,
            {co.ACTION: co.ACTION_KILL_TASK, co.RESULT_PIPE: self._request_pipe, co.CORRELATION_ID: correlation_id},
        )
        self._main_queue.put(item)
        return self._response_pipe.recv()

    def health_check(self) -> dict:
        """
        Check if Worker is UP and running.
        :return: Details about the event result
        """
        logger.logger.debug("Running event: health_check", event_details=self._event_details)
        result = co.CODE_OK
        return {co.RESULT: result}

    def add_trigger(self) -> dict:
        """
        Add Trigger.
        :return: Details about the event result
        """
        logger.logger.debug("Running event: add_trigger", event_details=self._event_details)
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
        logger.logger.debug("Running event: remove_trigger", event_details=self._event_details)
        item = util.PrioritizedItem(
            co.MEDIUM_PRIORITY,
            {co.ACTION: co.ACTION_REMOVE_TRIGGER, co.RESULT_PIPE: self._request_pipe, co.DATA: self._event_details},
        )
        self._main_queue.put(item)
        return self._response_pipe.recv()

    def list_triggers(self) -> dict:
        """
        List all Triggers on Listeners available on Worker.
        :return: Details about the event result
        """
        logger.logger.debug("Running event: list_triggers", event_details=self._event_details)
        item = util.PrioritizedItem(
            co.MEDIUM_PRIORITY, {co.ACTION: co.ACTION_LIST_TRIGGERS, co.RESULT_PIPE: self._request_pipe}
        )
        self._main_queue.put(item)
        return self._response_pipe.recv()

from click import echo
from typing import List
from threading import Thread, Lock, Event
from queue import PriorityQueue
import time
import traceback

from cryton.worker import consumer
from cryton.worker.utility import constants as co, logger, util
from cryton.worker.triggers import Listener, ListenerEnum, ListenerIdentifiersEnum
from cryton.lib.metasploit import MetasploitClientUpdated


class Worker:
    def __init__(
        self,
        rabbit_host: str,
        rabbit_port: int,
        rabbit_username: str,
        rabbit_password: str,
        worker_name: str,
        consumer_count: int,
        processor_count: int,
        max_retries: int,
        persistent: bool,
        require_metasploit: bool,
    ):
        """
        Worker processes internal requests using self._main_queue and communicates with RabbitMQ server using Consumer.
        :param rabbit_host: Rabbit's server port
        :param rabbit_port: Rabbit's server host
        :param rabbit_username: Rabbit's username
        :param rabbit_password: Rabbit's password
        :param worker_name: Worker name (prefix) for queues
        :param consumer_count: How many consumers to use for queues
        (higher == faster RabbitMQ requests consuming, but heavier processor usage)
        :param processor_count: How many processors to use for internal requests
        (higher == more responsive internal requests processing, but heavier processor usage)
        :param max_retries: How many times to try to connect
        :param persistent: Keep Worker alive and keep on trying forever (if True)
        :param require_metasploit: Require Metasploit on startup and keep on trying forever (if True)
        """
        self._name = worker_name
        self._require_metasploit = require_metasploit
        self._listeners: List[Listener] = []
        self._triggers_lock = Lock()  # Lock to prevent modifying, while performing time-consuming actions.
        self._stopped = Event()
        self._main_queue = PriorityQueue()
        self._processor_count = processor_count if processor_count > 0 else 1
        self._consumer = consumer.Consumer(
            self._main_queue,
            rabbit_host,
            rabbit_port,
            rabbit_username,
            rabbit_password,
            worker_name,
            consumer_count,
            max_retries,
            persistent,
        )

    def start(self) -> None:
        """
        Start Consumer and processors in thread and keep self alive.
        :return: None
        """
        logger.logger.debug("Worker started.", processor_count=self._processor_count, consumer=str(self._consumer))
        echo(f"Starting Worker {self._name}..")
        echo("To exit press CTRL+C")
        try:
            self._check_metasploit_connection()
            self._start_consumer()
            self._start_threaded_processors()
            while not self._stopped.is_set() and self._consumer.is_running():  # Keep self alive and check for stops.
                time.sleep(5)

        except KeyboardInterrupt:
            pass

        self.stop()

    def _check_metasploit_connection(self):
        echo("Trying to connect to Metasploit.. ", nl=False)
        msf_client = MetasploitClientUpdated(log_in=False)

        while True:
            try:
                connected = msf_client.health.rpc.check()
                if connected:
                    echo("OK")
                    break
                elif not connected and not self._require_metasploit:
                    echo("FAIL")
                    return
            except Exception as ex:
                if not self._require_metasploit:
                    echo(f"FAIL ({ex})")
                    return

        echo("Trying to log in to Metasploit.. ", nl=False)
        try:
            msf_client.login()
        except Exception as ex:
            echo("FAIL")
            logger.logger.warning(f"Unable to login to the MSF RPC server - wrong credentials? Original error: {ex}")
            if self._require_metasploit:
                raise RuntimeError(f"Unable to login to the MSF RPC server - wrong credentials? Original error: {ex}")
        else:
            echo("OK")

    def stop(self) -> None:
        """
        Stop Worker (self). Stop Consumer, processors and triggers.
        :return: None
        """
        logger.logger.info("Stopping Worker", processor_count=self._processor_count, consumer=str(self._consumer))
        echo("Exiting..")
        self._consumer.stop()
        self._stopped.set()
        self._stop_threaded_processors()
        self._stop_listeners()

    def _start_threaded_processors(self) -> None:
        """
        Start processors in thread.
        :return: None
        """
        logger.logger.debug("Starting threaded processors.", processor_count=self._processor_count)
        for i in range(self._processor_count):
            thread = Thread(target=self._threaded_processor, kwargs={"thread_id": i + 1}, name=f"Thread-{i}-processor")
            thread.start()

    def _stop_threaded_processors(self) -> None:
        """
        Stop processors by sending shutdown request.
        :return: None
        """
        logger.logger.debug("Stopping threaded processors.", processor_count=self._processor_count)
        for _ in range(self._processor_count):
            item = util.PrioritizedItem(co.LOW_PRIORITY, {co.ACTION: co.ACTION_SHUTDOWN_THREADED_PROCESSOR})
            self._main_queue.put(item)

    def _start_consumer(self) -> None:
        """
        Start Consumer in thread.
        :return: None
        """
        logger.logger.debug("Starting self._consumer in Thread.", consumer=str(self._consumer))
        thread = Thread(target=self._consumer.start)
        thread.start()

    def _stop_listeners(self) -> None:
        """
        Stop all Listeners in self._listeners.
        :return: None
        """
        logger.logger.debug("Stopping all Listeners.")
        with self._triggers_lock:
            while len(self._listeners) > 0:
                listener_obj = self._listeners.pop(-1)
                listener_obj.stop()

    def _threaded_processor(self, thread_id: int) -> None:
        """
        Start a processor for request processing.
        :param thread_id: Fictional thread (processor) ID
        :return: None
        """
        logger.logger.debug("Threaded processor started.", thread_id=thread_id)
        while not self._stopped.is_set():
            request: util.PrioritizedItem = self._main_queue.get()
            try:
                request_action = request.item.pop(co.ACTION)
            except KeyError as ex:
                logger.logger.warning("Request doesn't contain action.", request=request, error=str(ex))
                continue

            try:  # Try to get method reference.
                action_callable = getattr(self, request_action)
            except AttributeError:
                if request_action == co.ACTION_SHUTDOWN_THREADED_PROCESSOR:
                    logger.logger.debug("Shutting down threaded processor.", thread_id=thread_id)
                    break
                logger.logger.warning("Request contains unknown action.", request=request)
                continue

            try:  # Try to call method and process the request.
                action_callable(request.item)
            except Exception as ex:
                logger.logger.warning("Request threw an exception in the process.", request=request, error=str(ex))
                logger.logger.debug(
                    "Request threw an exception in the process.",
                    request=request,
                    error=str(ex),
                    traceback=traceback.format_exc(),
                )
                continue

        logger.logger.debug("Threaded processor stopped.", thread_id=thread_id)

    def _kill_task(self, request: dict) -> None:
        """
        Process; Kill running Task using correlation_id.
        :param request: Data needed for process (Must contain: co.RESULT_PIPE, co.CORRELATION_ID)
        :return: None
        """
        logger.logger.debug("Calling process _kill_task", request=request)
        result_pipe = request.pop(co.RESULT_PIPE)
        correlation_id = request.pop(co.CORRELATION_ID)

        task_obj = self._consumer.pop_task(correlation_id)
        if task_obj is None:  # Task doesn't exist.
            err = "Couldn't find the Task."
            logger.logger.debug(err, correlation_id=correlation_id)
            result = {co.RESULT: co.CODE_ERROR, co.OUTPUT: err}

        else:  # Task found.
            try:
                kill_action = task_obj.kill()
                result = {co.RESULT: co.CODE_OK if kill_action else co.CODE_ERROR}

            except Exception as ex:
                logger.logger.debug("Couldn't kill the Task.", task_correlation_id=correlation_id, error=str(ex))
                result = {co.RESULT: co.CODE_ERROR, co.OUTPUT: str(ex)}

        result_pipe.send(result)
        logger.logger.debug("Finished process _kill_task", result=result)

    def _finish_task(self, request: dict) -> None:
        """
        Process; Delete Task from Consumer's Tasks list.
        :param request: Data needed for process (Must contain: co.CORRELATION_ID)
        :return: None
        """
        logger.logger.debug("Calling process _finish_task", request=request)
        correlation_id = request.pop(co.CORRELATION_ID)
        self._consumer.pop_task(correlation_id)
        logger.logger.debug("Finished process _finish_task")

    def _send_message(self, request: dict) -> None:
        """
        Process; Use Consumer to send a message.
        :param request: Data needed for process (Must contain: co.QUEUE_NAME, co.DATA, co.PROPERTIES)
        :return: None
        """
        logger.logger.debug("Calling process _send_message", request=request)
        queue_name = request.pop(co.QUEUE_NAME)
        msg_body = request.pop(co.DATA)
        msg_properties = request.pop(co.PROPERTIES)

        msg_properties.update(co.DEFAULT_MSG_PROPERTIES)
        self._consumer.send_message(queue_name, msg_body, msg_properties)
        logger.logger.debug("Finished process _send_message")

    def _add_trigger(self, request: dict) -> None:
        """
        Process; Add trigger and optionally create Listener, if it doesn't already exist.
        :param request: Data needed for process (Must contain: co.RESULT_PIPE, co.DATA)
        :return: None
        """
        logger.logger.debug("Calling process _add_trigger", request=request)
        result_pipe = request.pop(co.RESULT_PIPE)
        trigger_data = request.pop(co.DATA)

        listener_type = ListenerEnum[trigger_data.get(co.TRIGGER_TYPE)]
        with self._triggers_lock:  # Try to find specified Listener.
            for listener_obj in self._listeners:
                if listener_obj.compare_identifiers(trigger_data):
                    logger.logger.debug(
                        "Found existing Listener", type=listener_type, listener_triggers=listener_obj.get_triggers()
                    )
                    break
            else:  # If Listener doesn't exist, create new one.
                logger.logger.debug("Creating new Listener", type=listener_type)
                # Decides which listener identifiers to parse from trigger_data based on Listener type
                listener_identifiers = {
                    key: value
                    for key, value in trigger_data.items()
                    if key in ListenerIdentifiersEnum[trigger_data.get(co.TRIGGER_TYPE)]
                }
                listener_obj = listener_type(self._main_queue, **listener_identifiers)
                self._listeners.append(listener_obj)

        try:
            trigger_id = listener_obj.add_trigger(trigger_data)
        except Exception as ex:
            # raised mostly during MSF module execution
            result = {co.RESULT: co.CODE_ERROR, co.OUTPUT: str(ex)}
        else:
            result = {co.RESULT: co.CODE_OK, co.TRIGGER_ID: trigger_id}

        result_pipe.send(result)
        logger.logger.debug("Finished process _add_trigger", result=result)

    def _remove_trigger(self, request: dict) -> None:
        """
        Process; Remove trigger and optionally delete Listener, if it doesn't have any more triggers.
        :param request: Data needed for process (Must contain: co.RESULT_PIPE, co.DATA)
        :return: None
        """
        logger.logger.debug("Calling process _remove_trigger", request=request)
        result_pipe = request.pop(co.RESULT_PIPE)
        data = request.pop(co.DATA)

        trigger_id = data.get(co.TRIGGER_ID)
        with self._triggers_lock:  # Try to find specified Listener.
            for listener_obj in self._listeners:
                trigger = listener_obj.find_trigger(trigger_id)
                if trigger is not None:  # Remove trigger from Listener. Optionally remove listener completely.
                    logger.logger.debug("Found existing trigger", id=trigger_id)
                    listener_obj.remove_trigger(trigger)
                    if not listener_obj.any_trigger_exists():
                        self._listeners.remove(listener_obj)
                    result = {co.RESULT: co.CODE_OK}
                    break

            else:  # If Listener doesn't exist, replace it with None.
                logger.logger.debug("Existing trigger not found", id=trigger_id)
                result = {co.RESULT: co.CODE_ERROR, co.OUTPUT: "Existing trigger not found."}

        result_pipe.send(result)
        logger.logger.debug("Finished process _remove_trigger", result=result)

    def _list_triggers(self, request: dict) -> None:
        """
        Process; List Triggers (triggers).
        :param request: Data needed for process (Must contain: co.RESULT_PIPE)
        :return: None
        """
        logger.logger.debug("Calling process _list_triggers", request=request)
        result_pipe = request.pop(co.RESULT_PIPE)

        with self._triggers_lock:
            all_triggers = []
            for listener_obj in self._listeners:
                all_triggers.extend(listener_obj.get_triggers())

        result = {co.RESULT: co.CODE_OK, co.TRIGGER_LIST: all_triggers}
        result_pipe.send(result)
        logger.logger.debug("Finished process _list_triggers", result=result)

import json
import time
from threading import Thread, Event
from multiprocessing import Process, Queue, Manager, Pipe
from multiprocessing.managers import SyncManager
from queue import Empty
import amqpstorm
from traceback import format_exc
from structlog.stdlib import BoundLogger

from cryton.hive.utility import constants, logger, states, event, rabbit_client
from cryton.hive.models import stage, plan, step, run
from cryton.hive.config.settings import SETTINGS
from cryton.hive.cryton_app.models import CorrelationEventModel
from cryton.hive.services.scheduler import SchedulerService

from django.utils import timezone


class ChannelConsumer:
    def __init__(self, identifier: int, connection: amqpstorm.Connection, queues: dict, consumer_logger: BoundLogger):
        self._logger = consumer_logger.bind(channel_consumer_id=identifier)
        self._id = identifier
        self._channel = connection.channel()

        self._channel.basic.qos(1)
        for queue, callback in queues.items():  # Consume on each queue.
            self._channel.queue.declare(queue)
            self._channel.basic.consume(callback, queue)

    def start(self):
        self._logger.debug("channel consumer started")
        while not self._channel.is_closed:
            try:
                self._channel.start_consuming()

            except amqpstorm.AMQPConnectionError as ex:
                self._logger.debug("channel consumer encountered a connection error", error=str(ex))
                break

            except Exception as ex:  # If any uncaught exception occurs, channel consumer will still work
                self._logger.warning("channel consumer encountered an error", error=str(ex))
                self._logger.debug("channel consumer encountered an error", traceback=format_exc())

        self._logger.debug("channel consumer stopped")


class Consumer:
    def __init__(self, identifier: int, queue: Queue, queues: dict, channel_consumer_count: int):
        """
        Consumer takes care of the connection between Hive and RabbitMQ server and launching callbacks for the
        defined queues.
        :param identifier: consumer ID
        :param queues: Queues to consume
        :param channel_consumer_count: How many consumers to use for queues
            (higher == faster == heavier processor usage)
        """
        self._logger = logger.logger.bind(consumer_id=identifier)
        self._id = identifier
        self._queue = queue
        self._queues = queues
        self._channel_consumer_count = channel_consumer_count if channel_consumer_count > 0 else 1

        self._hostname = SETTINGS.rabbit.host
        self._port = SETTINGS.rabbit.port
        self._username = SETTINGS.rabbit.username
        self._password = SETTINGS.rabbit.password

        self._stopped = Event()
        self._connection: amqpstorm.Connection | None = None
        self._process: Process | None = None

    def start(self) -> None:
        """
        Start self in a process.
        :return: None
        """
        self._process = Process(target=self)
        self._process.start()

    def check_if_finished(self) -> None:
        """
        Wait for the process to finish.
        :return: None
        """
        self._process.join()

    def __call__(self) -> None:
        """
        Establish connection, start channel consumers in thread and keep self alive.
        :return: None
        """
        self._logger.debug("consumer started", channel_consumer_count=self._channel_consumer_count)
        self._stopped.clear()

        while not self._stopped.is_set():  # Keep self and connection alive and check for stop.
            try:
                if self._update_connection():
                    self._start_channel_consumers()

                if self._queue.get(timeout=5) is None:
                    self.stop()

            except amqpstorm.AMQPConnectionError:
                pass

            except Empty:
                pass

            except KeyboardInterrupt:
                pass

    def stop(self) -> None:
        """
        Stop Consumer (self). Close connection and its channels.
        :return: None
        """
        self._logger.debug("stopping consumer")
        self._stopped.set()

        if self._connection is not None and self._connection.is_open:  # Close connection and its channels.
            self._logger.debug("closing channels")

            for channel in list(self._connection.channels.values()):
                channel.close()

            self._logger.debug("closing connection")
            self._connection.close()

        self._logger.debug("consumer stopped")

    def _update_connection(self) -> bool:
        """
        Check existing connection for errors and optionally reconnect.
        :return: True if connection was updated
        :raises: amqpstorm.AMQPConnectionError if connection can't be established
        """
        try:  # If connection is missing or there is some other problem, raise exception
            if self._connection is None:
                raise amqpstorm.AMQPConnectionError("Connection does not exist.")

            if not self._connection.is_open:
                raise amqpstorm.AMQPConnectionError("Connection is closed.")

            self._connection.check_for_errors()

            return False

        except amqpstorm.AMQPError as ex:  # Try to establish connection on error
            self._logger.warning("no connection to rabbitmq server", error=str(ex))
            self._connection = amqpstorm.Connection(self._hostname, self._username, self._password, self._port)
            self._logger.info("connection to RabbitMQ server established")

        return True

    def _start_channel_consumers(self) -> None:
        """
        Start channel consumers in threads.
        :return: None
        """
        self._logger.debug("starting channel consumers", channel_consumer_count=self._channel_consumer_count)
        for i in range(self._channel_consumer_count):
            channel_consumer = ChannelConsumer(i + 1, self._connection, self._queues, self._logger)
            thread = Thread(target=channel_consumer.start, name=f"Thread-{i}-consumer")
            thread.start()


class Listener:
    def __init__(self):
        """
        Listener.
        """
        self._logger = logger.logger.bind()
        self._consumers: list[Consumer] = []
        self.consumers_count = SETTINGS.cpu_cores

        self._stopped = Event()

        self._manager: SyncManager = Manager()
        self._queue = self._manager.Queue()
        self._scheduler_job_queue = self._manager.Queue()

        self._scheduler = SchedulerService(self._scheduler_job_queue)

        self.rabbit_queues = {
            SETTINGS.rabbit.queues.attack_response: self.step_response_callback,
            SETTINGS.rabbit.queues.agent_response: self.step_response_callback,
            SETTINGS.rabbit.queues.event_response: self.event_callback,
            SETTINGS.rabbit.queues.control_request: self.control_request_callback,
        }

    def start(self, blocking: bool = True) -> None:
        """
        Start and keep self alive.
        :param blocking: Whether the listener should be blocking the execution
        :return: None
        """
        self._start_consumers()
        self._scheduler.start()

        try:
            while blocking and not self._stopped.is_set():
                time.sleep(5)
        except KeyboardInterrupt:
            print("keyboard interrupt")
            self.stop()

    def stop(self) -> None:
        """
        Stop Listener and it's Consumers.
        :return: None
        """
        for _ in range(len(self._consumers) + 1):
            self._queue.put(None)

        for consumer in self._consumers:
            consumer.check_if_finished()

        self._scheduler.stop()
        self._stopped.set()
        self._logger.info("stopped RabbitMQ listener")

    def _start_consumers(self) -> None:
        """
        Create and start consumers.
        :return: None
        """
        for i in range(self.consumers_count):
            consumer = Consumer(i, self._queue, self.rabbit_queues, SETTINGS.threads_per_process)
            consumer.start()
            self._consumers.append(consumer)

        self._logger.info("started RabbitMQ listener")

    def step_response_callback(self, message: amqpstorm.Message) -> None:
        """
        Callback for processing Step execution responses.
        :param message: Received RabbitMQ message
        :return: None
        """
        correlation_id = message.correlation_id
        local_logger = self._logger.bind(correlation_id=correlation_id)
        local_logger.debug("received step response callback")
        message.ack()

        # Get correlation event object from DB
        try:
            correlation_event_obj = self._get_correlation_event(correlation_id)
        except CorrelationEventModel.DoesNotExist:
            local_logger.warning("received nonexistent correlation_id")
            return

        # Create execution object and delete the correlation event
        step_ex_obj = step.StepExecution(correlation_event_obj.step_execution_id)
        correlation_event_obj.delete()

        # Process finished execution
        message_body = json.loads(message.body)
        local_logger.debug("processing finished execution", message_body=message_body)
        step_ex_obj.postprocess(message_body)  # Save result, output, sessions, etc.
        step_ex_obj.ignore_successors()  # Ignore successors depending on the result
        event.Event({"step_execution_id": step_ex_obj.model.id}).handle_finished_step()  # Handle FINISHED states

        # Check if execution is being paused, otherwise execute successors if StepExecution is in FINISHED state
        plan_state = plan.PlanExecution(step_ex_obj.model.stage_execution.plan_execution_id).state
        if plan_state == states.PAUSING:
            self._handle_pausing(step_ex_obj)
        # Do not execute successors if the plan is stopping
        elif plan_state in [states.STOPPING, states.STOPPED]:
            pass
        elif step_ex_obj.state in [states.FINISHED, states.FAILED, states.ERROR]:
            step_ex_obj.start_successors()

    def event_callback(self, message: amqpstorm.Message) -> None:
        """
        Callback for processing events.
        :param message: Received RabbitMQ message
        :return: None
        """
        local_logger = self._logger.bind(correlation_id=message.correlation_id)
        local_logger.debug("received event callback")
        message.ack()

        message_body = json.loads(message.body)
        local_logger.debug("processing event callback", message_body=message_body)
        try:
            event_t = message_body[constants.EVENT_T]
            event_v = message_body[constants.EVENT_V]
        except (TypeError, KeyError):
            local_logger.warning("Event must contain event_t and event_v!")
            return

        if event_t == constants.EVENT_TRIGGER_STAGE:
            event.Event(event_v).trigger_stage()
        elif event_t == constants.EVENT_STEP_EXECUTION_ERROR:
            event.Event(event_v).handle_finished_step()
        else:
            local_logger.warning("nonexistent event received", event_t=event_t)

    def control_request_callback(self, message: amqpstorm.Message) -> None:
        """
        Callback for processing control requests.
        :param message: Received RabbitMQ message
        :return: None
        """
        local_logger = self._logger.bind(correlation_id=message.correlation_id)
        local_logger.debug("received control request callback")
        message.ack()

        message_body = json.loads(message.body)
        local_logger.debug("processing control request callback", message_body=message_body)
        result = -1
        try:
            event_t = message_body[constants.EVENT_T]
            event_v = message_body[constants.EVENT_V]
        except (TypeError, KeyError):
            local_logger.warning("control request must contain event_t and event_v!")
        else:
            if event_t == constants.EVENT_UPDATE_SCHEDULER:
                response_pipe, request_pipe = Pipe()
                self._scheduler_job_queue.put((event_v, request_pipe))
                result = response_pipe.recv()
            else:
                local_logger.warning("nonexistent event received", event_t=event_t)

        response = {constants.RETURN_VALUE: result}
        self._send_response(message, response)

    @staticmethod
    def _get_correlation_event(correlation_id: str) -> CorrelationEventModel:
        """
        Find correlation event.
        :param correlation_id: ID of the correlation event
        :return: correlation event
        :raises: CorrelationEventModel.DoesNotExist
        """
        # The correlation event may not be created yet, give it some time
        timeout = time.time() + SETTINGS.message_timeout
        while time.time() < timeout:
            try:
                return CorrelationEventModel.objects.get(correlation_id=correlation_id)
            except CorrelationEventModel.DoesNotExist:
                time.sleep(3)

        raise CorrelationEventModel.DoesNotExist()

    def _handle_pausing(self, step_ex_obj: step.StepExecution) -> None:
        """
        Check for PAUSED states.
        :param step_ex_obj: StepExecution object to check
        :return: None
        """
        self._logger.debug("handling pause", step_execution_id=step_ex_obj.model.id)

        # Pause Stage execution and successors only if it's in the PAUSING state
        stage_ex_obj = stage.StageExecution(step_ex_obj.model.stage_execution_id)
        if stage_ex_obj.state == states.PAUSING:
            step_ex_obj.pause_successors()  # Pause all successors so they can be executed after RESUME

            # If any Steps are still running/starting, no execution can be paused
            if stage_ex_obj.model.step_executions.filter(state__in=[states.STARTING, states.RUNNING]).exists():
                return

            stage_ex_obj.state = states.PAUSED
            stage_ex_obj.pause_time = timezone.now()
            self._logger.info("stage execution paused", stage_execution_id=stage_ex_obj.model.id)

        # Check if Plan execution should be paused since the Stage execution could have finished
        plan_ex_obj = plan.PlanExecution(stage_ex_obj.model.plan_execution_id)
        if (
            plan_ex_obj.state == states.PAUSING
            and not plan_ex_obj.model.stage_executions.all().exclude(state__in=states.PLAN_STAGE_PAUSE_STATES).exists()
        ):
            plan_ex_obj.state = states.PAUSED
            plan_ex_obj.pause_time = timezone.now()
            self._logger.info("plan execution paused", plan_execution_id=plan_ex_obj.model.id)

            run_obj = run.Run(plan_ex_obj.model.run_id)
            if (
                run_obj.state == states.PAUSING
                and not run_obj.model.plan_executions.all()
                .exclude(state__in=states.PLAN_FINAL_STATES + states.PLAN_RESUME_STATES)
                .exists()
            ):
                run_obj.state = states.PAUSED
                run_obj.pause_time = timezone.now()
                self._logger.info("run paused", run_id=run_obj.model.id)

    @staticmethod
    def _send_response(original_message: amqpstorm.Message, message_body: dict) -> None:
        """
        Send a response to `reply_to` from the original message.
        :param original_message: Received message
        :param message_body: Message content
        :return: None
        """
        properties = {"correlation_id": original_message.correlation_id}
        with rabbit_client.Client(original_message.channel) as client:
            client.send_message(original_message.reply_to, message_body, properties)

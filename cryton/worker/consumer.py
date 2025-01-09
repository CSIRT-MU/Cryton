from click import echo
import amqpstorm
import json
import time
from threading import Thread, Lock, Event
from queue import PriorityQueue
from uuid import uuid1

from cryton.worker import task
from cryton.worker.utility import logger, util


class ChannelConsumer:
    def __init__(self, identifier: int, connection: amqpstorm.Connection, queues: dict):
        self._logger = logger.logger.bind(channel_consumer_id=identifier)
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

        self._logger.debug("channel consumer stopped")


class Consumer:
    def __init__(
        self,
        main_queue: PriorityQueue,
        rabbit_host: str,
        rabbit_port: int,
        rabbit_username: str,
        rabbit_password: str,
        worker_name: str,
        consumer_count: int,
        max_retries: int,
        persistent: bool,
    ):
        """
        Consumer takes care of the connection between Worker and RabbitMQ server and launching callbacks for the
        defined queues.
        Update Queues here and add _callback_queue method to this Class.
        :param main_queue: Worker's queue for internal request processing
        :param rabbit_host: Rabbit's server port
        :param rabbit_port: Rabbit's server host
        :param rabbit_username: Rabbit's username
        :param rabbit_password: Rabbit's password
        :param worker_name: Worker name (prefix) for queues
        :param consumer_count: How many consumers to use for queues (higher == faster, but heavier processor usage)
        :param max_retries: How many times to try to connect
        :param persistent: Keep Worker alive and keep on trying forever (if True)
        """
        self._logger = logger.logger.bind()
        # TODO: rename also the queues in the hive?
        attack_q = f"cryton.worker.{worker_name}.attack.request"  # TODO: rename to cryton.attack.request.{}?
        control_q = f"cryton.worker.{worker_name}.control.request"  # TODO: rename to cryton.control.request.{}?
        self._queues = {
            attack_q: self._callback_attack,
            control_q: self._callback_control,
        }

        self._hostname = rabbit_host
        self._port = rabbit_port
        self._username = rabbit_username
        self._password = rabbit_password
        self._max_retries = max_retries
        self._persistent = persistent
        self._main_queue = main_queue
        self._channel_consumer_count = consumer_count if consumer_count > 0 else 1
        self._stopped = Event()
        self._connection: amqpstorm.Connection | None = None
        self._tasks: list[task.Task] = []
        self._tasks_lock = Lock()  # Lock to prevent modifying, while performing time-consuming actions.
        self._undelivered_messages: list[util.UndeliveredMessage] = []

    def __str__(self) -> str:
        return f"{self._username}@{self._hostname}:{self._port}"

    def is_running(self) -> bool:
        return not self._stopped.is_set()

    # TODO: should run in a Process
    # TODO: resolve the KeyboardError to prevent t_consumer raise Exception on channel fail
    def start(self) -> None:
        """
        Establish connection, start channel consumers in thread and keep self alive.
        :return: None
        """
        self._logger.debug(
            "consumer started",
            hostname=self._hostname,
            port=self._port,
            username=self._username,
            queues=self._queues,
            max_retries=self._max_retries,
            persistent=self._persistent,
            channel_consumer_count=self._channel_consumer_count,
        )
        self._stopped.clear()

        while self.is_running():  # Keep self and connection alive and check for stop.
            try:
                if self._update_connection():
                    self._start_channel_consumers()
                    self._get_undelivered_task_replies()
                    self._redelivered_messages()
                time.sleep(5)

            except amqpstorm.AMQPConnectionError as ex:
                if self._persistent:
                    self._logger.debug("ignoring connection error due to persistent mode", error=str(ex))
                    echo("Due to persistent mode, Worker will try to reconnect util manual shutdown.")
                    continue
                self._stopped.set()
                echo("Stopping due to connection loss..")

    def stop(self) -> None:
        """
        Stop Consumer (self). Wait for running Tasks (optionally stop them), close connection and its channels.
        :return: None
        """
        self._logger.debug("stopping consumer")
        self._stopped.set()

        # Wait for Tasks to finish. Kill them on KeyboardInterrupt error.
        try:
            self._logger.debug("waiting for unfinished Tasks")
            echo("Waiting for running modules to finish.. press CTRL + C to stop them.")
            while len(self._tasks) > 0:
                time.sleep(1)

        except KeyboardInterrupt:
            self._logger.debug("stopping unfinished Tasks")
            echo("Forcefully stopping running modules..")
            with self._tasks_lock:
                for task_obj in self._tasks:
                    task_obj.stop()

        # Close connection and its channels.
        if self._connection is not None and self._connection.is_open:
            self._logger.debug("closing channels")
            echo("Closing connection and it's channels..")
            for channel in list(self._connection.channels.values()):
                channel.close()
            self._logger.debug("Closing connection.")
            self._connection.close()

        self._logger.debug("consumer stopped")

    def _update_connection(self) -> bool:
        """
        Check existing connection for errors and optionally reconnect.
        Debug logs aren't present since it creates not necessary information.
        :return: True if connection was updated
        """
        try:  # If connection is missing or there is some other problem, raise exception.
            if self._connection is None:
                raise amqpstorm.AMQPConnectionError("Connection does not exist.")

            if not self._connection.is_open:
                raise amqpstorm.AMQPConnectionError("Connection is closed.")

            self._connection.check_for_errors()
            return False

        except amqpstorm.AMQPError as ex:  # Try to establish connection or error.
            echo(f"{str(ex)} Retrying..")
            self._logger.warning("connection lost.", error=str(ex))
            self._create_connection()

        return True

    def _start_channel_consumers(self) -> None:
        """
        Start consumers in thread.
        :return: None
        """
        self._logger.debug("starting channel consumers", channel_consumer_count=self._channel_consumer_count)
        for i in range(self._channel_consumer_count):
            channel_consumer = ChannelConsumer(i + 1, self._connection, self._queues)
            thread = Thread(target=channel_consumer.start, name=f"Thread-{i}-consumer")
            thread.start()

    def _callback_attack(self, message: amqpstorm.Message) -> None:
        """
        Create new AttackTask and save it.
        :param message: Received RabbitMQ Message
        :return: None
        """
        self._logger.debug("attack callback", correlation_id=message.correlation_id, message_body=message.body)
        message.ack()
        task_obj = task.AttackTask(message, self._main_queue, self._connection)
        task_obj.start()
        with self._tasks_lock:
            self._tasks.append(task_obj)

    def _callback_control(self, message: amqpstorm.Message) -> None:
        """
        Create new ControlTask and save it.
        :param message: Received RabbitMQ Message
        :return: None
        """
        self._logger.debug("control callback", correlation_id=message.correlation_id, message_body=message.body)
        message.ack()
        task_obj = task.ControlTask(message, self._main_queue, self._connection)
        task_obj.start()
        with self._tasks_lock:
            self._tasks.append(task_obj)

    def _create_connection(self) -> None:
        """
        Try to create a connection to a RabbitMQ server.
        :raises: amqpstorm.AMQPConnectionError if connection can't be established
        :return: None
        """
        self._logger.debug("establishing connection")
        for attempt in range(self._max_retries):
            if not self.is_running():
                return

            try:  # Create connection.
                self._connection = amqpstorm.Connection(self._hostname, self._username, self._password, self._port)
                self._logger.debug("connection established")
                echo("Connection to RabbitMQ server established.")
                echo("[*] Waiting for messages.")
                return

            except amqpstorm.AMQPError as ex:
                self._logger.warning("connection couldn't be established", error=str(ex))
                echo(f"Connection couldn't be established. (attempt {attempt + 1}/{self._max_retries})")
                if attempt + 1 < self._max_retries:
                    time.sleep(min(attempt + 1 * 2, 30))

        self._logger.error("max number of retries reached")
        raise amqpstorm.AMQPConnectionError("Max number of retries reached.")

    def send_message(self, queue: str, message_body: dict | str, message_properties: dict) -> None:
        """
        Open a new channel and send a custom message.
        :param queue: Target queue (message receiver)
        :param message_body: Message content
        :param message_properties: Message properties (options)
        :return: None
        """
        self._logger.debug("sending message", queue=queue, message=message_body, properties=message_properties)
        if isinstance(message_body, dict):
            message_body = json.dumps(message_body)

        try:
            channel = self._connection.channel()
        except amqpstorm.AMQPError:
            local_logger = self._logger.bind(uuid=str(uuid1()))
            self._undelivered_messages.append(util.UndeliveredMessage(queue, message_body, message_properties))
            local_logger.error("unable to send the message", queue=queue)
            local_logger.debug("unable to send the message", message=message_body, properties=message_properties)
            return

        channel.queue.declare(queue)
        message = amqpstorm.Message.create(channel, message_body, message_properties)
        # TODO: publish can raise an error when a message is not acked, it also freezes until it raises and error due
        #  to a timeout (base rabbit message ack timeout)
        message.publish(queue)
        channel.close()
        self._logger.debug("message sent", queue=queue, message=message_body, properties=message_properties)

    def _redelivered_messages(self) -> None:
        """
        Send all undelivered messages.
        :return: None
        """
        self._logger.debug("redelivering messages")
        while self._undelivered_messages:
            message = self._undelivered_messages.pop(0)
            self.send_message(message.recipient, message.body, message.properties)

    def _get_undelivered_task_replies(self) -> None:
        """
        Get all undelivered Task messages and add them to the list.
        :return: None
        """
        self._logger.debug("getting undelivered tasks' messages")
        with self._tasks_lock:
            for task_obj in self._tasks:
                if messages := task_obj.undelivered_messages:
                    self._undelivered_messages.extend(messages)
                    self._tasks.remove(task_obj)

    def pop_task(self, correlation_id) -> task.Task | None:
        """
        Find a Task using correlation_id and remove it from tasks.
        :param correlation_id: Task's correlation_id
        :return: Task matching correlation_id, or None if none matched
        """
        self._logger.debug("popping (searching) task using correlation_id", correlation_id=correlation_id)
        with self._tasks_lock:
            for i in range(len(self._tasks)):
                if self._tasks[i].correlation_id == correlation_id:
                    self._logger.debug("task popping (search) succeeded", correlation_id=correlation_id)
                    return self._tasks.pop(i)

        self._logger.debug("task popping (search) failed", correlation_id=correlation_id)

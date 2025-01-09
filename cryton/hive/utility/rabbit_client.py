import amqpstorm
from uuid import uuid1
import time
import json

from cryton.hive.config.settings import SETTINGS
from cryton.hive.utility import constants, exceptions, logger


class RpcClient:
    def __init__(self, channel: amqpstorm.Channel = None):
        """
        Rabbit RPC client.
        :param channel: Existing RabbitMQ channel to use for communication
        """
        self.callback_queue = str(uuid1())
        self._logger = logger.logger.bind(callback_queue=self.callback_queue)

        self.connection: amqpstorm.Connection | None = None
        self.channel = channel

        self.response: dict | None = None
        self.correlation_id: str | None = None

        self.open()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self) -> None:
        """
        Setup connection, channel, and callback_queue.
        :return: None
        """
        if self.channel is None:  # Create new connection and channel if not given
            self._logger.debug("creating new channel and connection")
            self.connection = amqpstorm.Connection(
                SETTINGS.rabbit.host, SETTINGS.rabbit.username, SETTINGS.rabbit.password, SETTINGS.rabbit.port
            )
            self.channel = self.connection.channel()

        self._logger.debug("setting up channel (declare/consume)")
        self.channel.queue.declare(self.callback_queue)
        self.channel.basic.consume(self._on_response, no_ack=True, queue=self.callback_queue)

    def close(self) -> None:
        """
        Delete the callback_queue, optionally close created channel and connection.
        :return: None
        """
        self._logger.debug("removing callback_queue from channel")
        self.channel.queue.delete(self.callback_queue)

        if self.connection is not None:  # Stop channel and connection only if created new one was created.
            self._logger.debug("closing channel and connection")
            self.channel.close()
            self.connection.close()

    def call(
        self, target_queue: str, message_body: dict, properties: dict = None, custom_reply_queue: str = None
    ) -> dict:
        """
        Create RPC call and wait for response.
        :param target_queue: Target RabbitMQ queue to send the message
        :param message_body: Message contents
        :param properties: Message properties
        :param custom_reply_queue: Custom queue to send the reply to (moves self.callback_queue to msg_body[
        "ack_queue"] and is only used for message received acknowledgment)
        :return: Serialized response
        :raises: exceptions.RpcTimeoutError
        """
        self._logger.debug(
            "remote procedure call",
            correlation_id=self.correlation_id,
            target_queue=target_queue,
            message_body=message_body,
            custom_reply_queue=custom_reply_queue,
            properties=properties,
        )
        self._clean_up()
        self.channel.queue.declare(target_queue)

        message = self._create_message(message_body, properties, custom_reply_queue)
        message.publish(target_queue)

        self._wait_for_response()

        return self.response

    def _clean_up(self) -> None:
        """
        Remove message specific information.
        :return: None
        """
        self.response = None
        self.correlation_id = None

    def _create_message(
        self, message_body: dict, properties: dict = None, custom_reply_queue: str = None
    ) -> amqpstorm.Message:
        """
        Create message. Optionally use custom reply queue.
        :param message_body: Message contents
        :param properties: Message properties
        :param custom_reply_queue: Custom queue to send the reply to (moves self.callback_queue to msg_body[
        "ack_queue"] and is only used for message received acknowledgment)
        :return: Rabbit message
        """
        if custom_reply_queue is not None:
            message_body.update({constants.ACK_QUEUE: self.callback_queue})

        message = amqpstorm.Message.create(self.channel, json.dumps(message_body), properties)
        message.reply_to = custom_reply_queue if custom_reply_queue is not None else self.callback_queue
        self.correlation_id = message.correlation_id
        self._logger.debug("created message", correlation_id=self.correlation_id)

        return message

    def _wait_for_response(self) -> None:
        """
        Wait for response.
        :return: None
        :raises: exceptions.RpcTimeoutError
        """
        self._logger.debug("waiting for response")
        time_limit = time.time() + SETTINGS.message_timeout
        while self.response is None and time.time() < time_limit:
            self.channel.process_data_events()

        if self.response is None:
            self._logger.warning("couldn't get response in time")
            raise exceptions.RpcTimeoutError("Couldn't get response in time.")

    def _on_response(self, message: amqpstorm.Message) -> None:
        """
        Check if the correlation_id matches and save the response.
        :param message: Received RabbitMQ message
        :return: None
        """
        if self.correlation_id == message.correlation_id:
            self.response = message.json()
            return

        self._logger.warning(
            "received message with an unknown correlation_id",
            expected=self.correlation_id,
            received=message.correlation_id,
        )


class Client:
    def __init__(self, channel: amqpstorm.Channel = None):
        """
        Rabbit RPC client.
        :param channel: Existing RabbitMQ channel to use for communication
        """
        self._logger = logger.logger.bind(uuid=str(uuid1()))
        self.connection: amqpstorm.Connection | None = None
        self.channel = channel

        self.open()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self) -> None:
        """
        Setup connection and channel.
        :return: None
        """
        if self.channel is None:  # Create new connection and channel if not given
            self._logger.debug("Creating new channel and connection.")
            self.connection = amqpstorm.Connection(
                SETTINGS.rabbit.host, SETTINGS.rabbit.username, SETTINGS.rabbit.password, SETTINGS.rabbit.port
            )
            self.channel = self.connection.channel()

    def close(self) -> None:
        """
        Close created channel and connection.
        :return: None
        """
        if self.connection is not None:  # Stop channel and connection only if created new one was created.
            self._logger.debug("Closing channel and connection.")
            self.channel.close()
            self.connection.close()

    def send_message(self, target_queue: str, message_body: dict, properties: dict = None) -> None:
        """
        Declare the target queue and send a message.
        :param target_queue: Target RabbitMQ queue to send the message
        :param message_body: Message contents
        :param properties: Message properties
        :return: none
        """
        self._logger.debug("sending rabbitmq message.", target_queue=target_queue, message_body=message_body)
        self.channel.queue.declare(target_queue)

        message = amqpstorm.Message.create(self.channel, json.dumps(message_body), properties)
        message.publish(target_queue)

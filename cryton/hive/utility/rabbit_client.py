import amqpstorm
import uuid
import time
import json
from typing import Union

from cryton.hive.config.settings import SETTINGS
from cryton.hive.utility import constants, exceptions, logger


class RpcClient:
    def __init__(self, channel: amqpstorm.Channel = None):
        """
        Rabbit RPC client.
        :param channel: Existing RabbitMQ channel to use for communication
        """
        self.connection: Union[amqpstorm.Connection, None] = None
        self.channel = channel

        self.callback_queue = str(uuid.uuid1())
        self.timeout = SETTINGS.message_timeout

        self.response: Union[dict, None] = None
        self.correlation_id: Union[str, None] = None

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
            logger.logger.debug("Creating new channel and connection.", callback_queue=self.callback_queue)
            self.connection = amqpstorm.Connection(
                SETTINGS.rabbit.host, SETTINGS.rabbit.username, SETTINGS.rabbit.password, SETTINGS.rabbit.port
            )
            self.channel = self.connection.channel()

        logger.logger.debug("Setting up channel (declare/consume).", callback_queue=self.callback_queue)
        self.channel.queue.declare(self.callback_queue)
        self.channel.basic.consume(self._on_response, no_ack=True, queue=self.callback_queue)

    def close(self) -> None:
        """
        Delete the callback_queue, optionally close created channel and connection.
        :return: None
        """
        logger.logger.debug("Removing callback_queue from channel", callback_queue=self.callback_queue)
        self.channel.queue.delete(self.callback_queue)

        if self.connection is not None:  # Stop channel and connection only if created new one was created.
            logger.logger.debug("Closing channel and connection.", callback_queue=self.callback_queue)
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
        logger.logger.debug(
            "Remote procedure call.",
            correlation_id=self.correlation_id,
            target_queue=target_queue,
            message_body=message_body,
            custom_reply_queue=custom_reply_queue,
            properties=properties,
            callback_queue=self.callback_queue,
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
        logger.logger.debug("Created message.", correlation_id=self.correlation_id, callback_queue=self.callback_queue)

        return message

    def _wait_for_response(self) -> None:
        """
        Wait for response.
        :return: None
        :raises: exceptions.RpcTimeoutError
        """
        logger.logger.debug(
            "Waiting for response.", correlation_id=self.correlation_id, callback_queue=self.callback_queue
        )
        time_limit = time.time() + self.timeout
        while self.response is None and time.time() < time_limit:
            self.channel.process_data_events()

        if self.response is None:
            logger.logger.warning(
                "Couldn't get response in time.", correlation_id=self.correlation_id, callback_queue=self.callback_queue
            )
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

        logger.logger.warning(
            "Received message with an unknown correlation_id.",
            correlation_id=self.correlation_id,
            message_correlation_id=message.correlation_id,
            callback_queue=self.callback_queue,
        )


class Client:
    def __init__(self, channel: amqpstorm.Channel = None):
        """
        Rabbit RPC client.
        :param channel: Existing RabbitMQ channel to use for communication
        """
        self.connection: Union[amqpstorm.Connection, None] = None
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
            logger.logger.debug("Creating new channel and connection.")
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
            logger.logger.debug("Closing channel and connection.")
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
        logger.logger.debug("Sending RabbitMQ message.", target_queue=target_queue, message_body=message_body)
        self.channel.queue.declare(target_queue)

        message = amqpstorm.Message.create(self.channel, json.dumps(message_body), properties)
        message.publish(target_queue)

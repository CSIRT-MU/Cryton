from click import echo
from multiprocessing import Process, get_context, connection
from queue import PriorityQueue
from threading import Thread
import amqpstorm
import json
import traceback
from jsonschema import validate, ValidationError
from typing import Callable
from dataclasses import asdict
from importlib import import_module
from uuid import uuid1

from cryton.worker import event
from cryton.worker.utility import util, constants as co, logger
from cryton.lib.utility.module import ModuleOutput, Result


class Task:
    def __init__(self, message: amqpstorm.Message, main_queue: PriorityQueue, connection: amqpstorm.Connection):
        """
        Class for processing callbacks.
        :param message: Received RabbitMQ Message
        :param main_queue: Worker's queue for internal request processing
        """
        self.message = message
        self.correlation_id = message.correlation_id
        self._main_queue = main_queue
        self._process: Process | None = None
        self._connection = connection
        self.undelivered_messages: list[util.UndeliveredMessage] = []
        self._logger = logger.logger.bind(correlation_id=self.correlation_id)

    def start(self):
        """
        Run the Task in a thread.
        :return: None
        """
        Thread(target=self).start()

    def __call__(self) -> None:
        """
        Load message, execute callback and send reply.
        :return: None
        """
        self._logger.debug("processing task")
        echo(f"Processing Task. correlation_id: {self.correlation_id}")

        message_body = json.loads(self.message.body)

        # Confirm message was received if the ack_queue parameter is defined.
        if (ack_queue := message_body.get(co.ACK_QUEUE)) is not None:
            self.send_ack(ack_queue)

        try:
            self._validate(message_body)
        except ValidationError as ex:
            result = {co.RESULT: co.CODE_ERROR, co.OUTPUT: str(ex)}
        else:
            result = self._execute(message_body)

        result_json = json.dumps(result)
        reply_sent = self.reply(result_json)

        # TODO: instead of sending a message like this, it might be easier to go through the tasks and check if
        #   they're finished, less messages == better
        # Remove Task from Consumer
        if reply_sent:
            item = util.PrioritizedItem(
                co.HIGH_PRIORITY, {co.ACTION: co.ACTION_FINISH_TASK, co.CORRELATION_ID: self.correlation_id}
            )
            self._main_queue.put(item)

        echo(f"Finished Task processing. correlation_id: {self.correlation_id}")
        self._logger.debug("finished task processing")

    def _execute(self, message_body: dict) -> dict:
        """
        Custom execution for callback processing.
        :param message_body: Received RabbitMQ Message's
        :return: Execution's result
        """
        pass

    def _validate(self, message_body: dict) -> dict:
        """
        Custom validation for callback processing.
        :param message_body: Received RabbitMQ Message's
        :return: Validation's result
        """
        pass

    def _run_in_process(self, to_run: Callable, *args) -> ModuleOutput:
        """
        Run a method/callable in a new process.
        :param to_run: Callable to run
        :param args: Arguments to pass to the callable
        :return: Result from the callable or a custom one in case of an error
        """
        ctx = get_context("spawn")
        response_pipe, request_pipe = ctx.Pipe()
        # TODO: run in a logged process?
        self._process = ctx.Process(target=self._pipe_results, args=(request_pipe, to_run, *args))
        self._process.start()
        self._process.join()

        if self._process.exitcode == 0:
            result = response_pipe.recv()
        elif self._process.exitcode < 0:
            result = ModuleOutput(result=Result.STOPPED)
        else:
            result = ModuleOutput(Result.ERROR, "An unknown error occurred.")

        return result

    @staticmethod
    def _pipe_results(request_pipe: connection.Connection, to_run: Callable, *args) -> None:
        """
        Run a function and send its results into pipe.
        :param request_pipe: Pipe for results
        :param to_run: Callable to run
        :return: None
        """
        request_pipe.send(to_run(*args))

    def stop(self) -> bool:
        """
        Wrapper method for Process.kill() and send reply.
        :return: None
        """
        self._logger.debug("stopping task (its process)")
        if self._process is not None and self._process.pid is not None and self._process.exitcode is None:
            self._process.kill()
            return True
        return False

    def send_ack(self, ack_queue: str) -> None:
        """
        Send a custom message acknowledgment.
        :param ack_queue: On what queue to send the acknowledgment
        :return: None
        """
        msg_body = json.dumps({co.RESULT: co.CODE_OK})
        self.reply(msg_body, ack_queue)

    def reply(self, message_body: str, recipient: str = None) -> bool:
        """
        Update properties and send response.
        In case the channel contains errors, the message is saved.
        :param message_body: Content to be sent inside the message
        :param recipient: On which queue to send the message (default: message.reply_to)
        :return: True, if the message was sent
        """
        if recipient is None:
            recipient = self.message.reply_to

        properties = self.message.properties
        properties.update(co.DEFAULT_MSG_PROPERTIES)

        try:
            channel = self._connection.channel()
        except amqpstorm.AMQPError:
            local_logger = self._logger.bind(uuid=str(uuid1()))
            self.undelivered_messages.append(util.UndeliveredMessage(recipient, message_body, properties))
            local_logger.error("unable to send the message", recipient=recipient)
            local_logger.debug("unable to send the message", message_body=message_body)
            return False

        channel.queue.declare(recipient)

        message = amqpstorm.Message.create(channel, message_body, properties)
        message.publish(recipient)

        channel.close()

        self._logger.debug("reply sent", queue=recipient, body=message_body)
        return True


class AttackTask(Task):
    def __init__(self, message: amqpstorm.Message, main_queue: PriorityQueue, connection: amqpstorm.Connection):
        """
        Class for processing attack callbacks.
        :param message: Received RabbitMQ Message
        :param main_queue: Worker's queue for internal request processing
        """
        super().__init__(message, main_queue, connection)

    def _validate(self, message_body: dict) -> None:
        """
        Custom validation for callback processing.
        :param message_body: Received RabbitMQ Message's
        :return: None
        """
        schema = {  # TODO: this is the same as in hive...schemas.py
            "type": "object",
            "properties": {
                co.ACK_QUEUE: {"type": "string"},
                co.MODULE: {"type": "string"},
                co.ARGUMENTS: {"type": "object"},
            },
            "required": [co.ACK_QUEUE, co.MODULE, co.ARGUMENTS],
        }
        validate(message_body, schema)

    def _execute(self, message_body: dict) -> dict:
        """
        Custom execution for attack callback processing.
        Confirm that message was received, update properties and execute module.
        :param message_body: Received RabbitMQ Message's
        :return: Execution's result
        """
        self._logger.debug("running attacktask._execute()")
        module = message_body.pop(co.MODULE)
        arguments = message_body.pop(co.ARGUMENTS)
        result = asdict(self._run_in_process(util.run_module, *(module, arguments)))
        self._logger.debug("finished attacktask._execute()")

        return result


class ControlTask(Task):
    def __init__(self, message: amqpstorm.Message, main_queue: PriorityQueue, connection: amqpstorm.Connection):
        """
        Class for processing control callbacks.
        :param message: Received RabbitMQ Message
        :param main_queue: Worker's queue for internal request processing
        """
        super().__init__(message, main_queue, connection)

    def _validate(self, message_body: dict) -> None:
        """
        Custom validation for callback processing.
        :param message_body: Received RabbitMQ Message's
        :return: None
        """
        schema = {  # TODO: this is the same as in hive...schemas.py rework with triggers?
            "type": "object",
            "properties": {"event_t": {"type": "string"}},
            "required": ["event_t"],
            "allOf": [
                {
                    "if": {"properties": {"event_t": {"const": "VALIDATE_MODULE"}}, "required": ["event_t"]},
                    "then": {
                        "properties": {
                            "event_v": {
                                "type": "object",
                                "properties": {co.MODULE: {"type": "string"}, co.ARGUMENTS: {"type": "object"}},
                                "required": [co.MODULE, co.ARGUMENTS],
                            }
                        },
                        "required": ["event_v"],
                    },
                },
                {
                    "if": {"properties": {"event_t": {"const": "STOP_STEP_EXECUTION"}}, "required": ["event_t"]},
                    "then": {
                        "properties": {
                            "event_v": {"type": "object", "properties": {"correlation_id": {"type": "string"}}}
                        },
                        "required": ["event_v"],
                    },
                },
                {
                    "if": {"properties": {"event_t": {"const": "HEALTH_CHECK"}}, "required": ["event_t"]},
                    "then": {
                        "properties": {"event_v": {"type": "object"}},
                        "required": ["event_v"],
                    },
                },
                {
                    "if": {"properties": {"event_t": {"const": "ADD_TRIGGER"}}, "required": ["event_t"]},
                    "then": {
                        "anyOf": [
                            {
                                "properties": {
                                    "event_v": {
                                        "type": "object",
                                        "properties": {
                                            "trigger_type": {"type": "string"},
                                            "reply_to": {"type": "string"},
                                        },
                                    },
                                },
                            },
                            {
                                "properties": {
                                    "event_v": {
                                        "type": "object",
                                        "properties": {
                                            "host": {"type": "string"},
                                            "port": {"type": "integer"},
                                            "routes": {
                                                "description": "List of routes the listener will check for requests.",
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "path": {"type": "string", "description": "Request's path."},
                                                        "method": {
                                                            "type": "string",
                                                            "description": "Request's allowed method.",
                                                        },
                                                        "parameters": {
                                                            "description": "Request's required parameters.",
                                                            "type": "array",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "name": {
                                                                        "type": "string",
                                                                        "description": "Parameter's name.",
                                                                    },
                                                                    "value": {
                                                                        "type": "string",
                                                                        "description": "Parameter's value.",
                                                                    },
                                                                },
                                                                "required": ["name", "value"],
                                                                "additionalProperties": False,
                                                            },
                                                            "minItems": 1,
                                                        },
                                                    },
                                                    "required": ["path", "method", "parameters"],
                                                    "additionalProperties": False,
                                                },
                                                "minItems": 1,
                                            },
                                        },
                                    }
                                },
                            },
                            {
                                "properties": {
                                    "event_v": import_module("cryton.modules.metasploit.module").Module.SCHEMA
                                },
                            },
                        ]
                    },
                },
                {
                    "if": {"properties": {"event_t": {"const": "REMOVE_TRIGGER"}}, "required": ["event_t"]},
                    "then": {
                        "properties": {"event_v": {"type": "object", "properties": {"trigger_id": {"type": "string"}}}},
                        "required": ["event_v"],
                    },
                },
            ],
        }
        validate(message_body, schema)

    def _execute(self, message_body: dict) -> dict:
        """
        Custom execution for control callback processing.
        Process control event.
        :param message_body: Received RabbitMQ Message's
        :return: Execution's result
        """
        self._logger.debug("running controltask._execute()")
        event_t = message_body.pop(co.EVENT_T)
        event_obj = event.Event(message_body.pop(co.EVENT_V), self._main_queue)

        try:  # Get event callable and execute it.
            event_t_lower = event_t.lower()
            event_obj_method = getattr(event_obj, event_t_lower)
        except AttributeError:
            ex = f"Unknown event type: {event_t}."
            event_v = {co.RESULT: co.CODE_ERROR, co.OUTPUT: ex}
            self._logger.debug(ex)
        else:
            try:
                event_v = event_obj_method()
            except Exception as ex:
                event_v = {
                    co.OUTPUT: {
                        "ex_type": str(ex.__class__),
                        "error": ex.__str__(),
                        "traceback": traceback.format_exc(),
                    }
                }

        self._logger.debug("finished controltask._execute()")
        return {co.EVENT_T: event_t, co.EVENT_V: event_v}

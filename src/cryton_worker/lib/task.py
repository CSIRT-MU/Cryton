from click import echo
from multiprocessing import Process, get_context
from queue import PriorityQueue
from threading import Thread
import amqpstorm
import json
import traceback
from schema import Schema, Or, SchemaError, Optional as SchemaOptional
from utinni import EmpireLoginError
import asyncio
from typing import Optional, Callable, List

from cryton_worker.lib import event, empire
from cryton_worker.lib.util import util, constants as co, logger


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
        self._process: Optional[Process] = None
        self._connection = connection
        self.undelivered_messages: List[util.UndeliveredMessage] = []

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
        logger.logger.debug("Processing Task.", correlation_id=self.correlation_id)
        echo(f"Processing Task. correlation_id: {self.correlation_id}")

        message_body = json.loads(self.message.body)

        # Confirm message was received if the ack_queue parameter is defined.
        if (ack_queue := message_body.get(co.ACK_QUEUE)) is not None:
            self.send_ack(ack_queue)

        try:
            self._validate(message_body)
        except SchemaError as ex:
            result = {co.RETURN_CODE: co.CODE_ERROR, co.OUTPUT: str(ex)}
        else:
            result = self._execute(message_body)

        result_json = json.dumps(result)
        reply_sent = self.reply(result_json)

        # TODO: instead of sending a message like this, it might be easier to go through the tasks and check if
        #   they're finished, less messages == better
        # Remove Task from Consumer
        if reply_sent:
            item = util.PrioritizedItem(co.HIGH_PRIORITY, {co.ACTION: co.ACTION_FINISH_TASK,
                                                           co.CORRELATION_ID: self.correlation_id})
            self._main_queue.put(item)

        echo(f"Finished Task processing. correlation_id: {self.correlation_id}")
        logger.logger.debug("Finished Task processing.", correlation_id=self.correlation_id)

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

    def _run_in_process(self, to_run: Callable, *args):
        """
        Run a method/callable in a new process.
        :param to_run: Callable to run
        :param args: Arguments to pass to the callable
        :return: Result from the callable or a custom one in case of an error
        """
        ctx = get_context('spawn')
        response_pipe, request_pipe = ctx.Pipe()
        self._process = ctx.Process(target=to_run, args=(*args, request_pipe))  # TODO: run in a logged process?
        self._process.start()
        self._process.join()

        if self._process.exitcode == 0:
            result = response_pipe.recv()
        elif self._process.exitcode < 0:
            result = {co.RETURN_CODE: co.CODE_KILL}
        else:
            result = {co.RETURN_CODE: co.CODE_ERROR, co.OUTPUT: "An unknown error occurred."}

        return result

    def kill(self) -> bool:
        """
        Wrapper method for Process.kill() and send reply.
        :return: None
        """
        logger.logger.debug("Killing Task (its process).", correlation_id=self.correlation_id)
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
        msg_body = json.dumps({co.RETURN_CODE: co.CODE_OK})
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
            self.undelivered_messages.append(util.UndeliveredMessage(recipient, message_body, properties))
            logger.logger.error("Unable to send the message.", recipient=recipient, message=message_body,
                                properties=properties)
            return False

        channel.queue.declare(recipient)

        message = amqpstorm.Message.create(channel, message_body, properties)
        message.publish(recipient)

        channel.close()

        logger.logger.debug("Reply sent.", correlation_id=self.correlation_id, queue=recipient, body=message_body)
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
        validation_schema = Schema({
            co.ACK_QUEUE: str,
            co.STEP_TYPE: Or(
                co.STEP_TYPE_WORKER_EXECUTE, co.STEP_TYPE_EMPIRE_EXECUTE
            ),
            co.ARGUMENTS: Or(
                {
                    SchemaOptional(co.USE_NAMED_SESSION): str,
                    SchemaOptional(co.CREATE_NAMED_SESSION): str,
                    SchemaOptional(co.USE_ANY_SESSION_TO_TARGET): str,
                    co.MODULE: str,
                    co.MODULE_ARGUMENTS: dict,
                },
                {
                    co.USE_AGENT: str,
                    co.MODULE: str,
                    SchemaOptional(co.MODULE_ARGUMENTS): dict
                },
                {
                    co.USE_AGENT: str,
                    co.EMPIRE_SHELL_COMMAND: str,
                }
            )
        })

        validation_schema.validate(message_body)

    def _execute(self, message_body: dict) -> dict:
        """
        Custom execution for attack callback processing.
        Confirm that message was received, update properties and execute module.
        :param message_body: Received RabbitMQ Message's
        :return: Execution's result
        """
        logger.logger.info("Running AttackTask._execute().", correlation_id=self.correlation_id)

        # Extract needed data.
        step_type = message_body.pop(co.STEP_TYPE)
        arguments = message_body.pop(co.ARGUMENTS, {})

        # Start module execution.
        if step_type == co.STEP_TYPE_EMPIRE_EXECUTE:
            empire_client = empire.EmpireClient()
            try:
                result = asyncio.run(empire_client.execute_on_agent(arguments))
            except ConnectionError as err:
                result = {co.RETURN_CODE: -2, co.OUTPUT: str(err)}

        else:
            module_path = arguments.pop(co.MODULE)
            module_arguments = arguments.pop(co.MODULE_ARGUMENTS)
            result = self._run_in_process(util.run_attack_module, *(module_path, module_arguments))

        logger.logger.info("Finished AttackTask._execute().", correlation_id=self.correlation_id, step_type=step_type)
        return result


class AgentTask(Task):
    def __init__(self, message: amqpstorm.Message, main_queue: PriorityQueue, connection: amqpstorm.Connection):
        """
        Class for processing agent callbacks.
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
        validation_schema = Schema({
            co.ACK_QUEUE: str,
            co.STEP_TYPE: co.STEP_TYPE_DEPLOY_AGENT,
            co.ARGUMENTS:
                {
                    SchemaOptional(co.SESSION_ID): str,
                    SchemaOptional(co.USE_NAMED_SESSION): str,
                    SchemaOptional(co.USE_ANY_SESSION_TO_TARGET): str,
                    SchemaOptional(co.SSH_CONNECTION): dict,
                    co.EMPIRE_LISTENER_NAME: str,
                    co.STAGER_TYPE: str,
                    co.AGENT_NAME: str,
                    SchemaOptional(co.EMPIRE_LISTENER_TYPE): str,
                    SchemaOptional(co.EMPIRE_LISTENER_PORT): int,
                    SchemaOptional(co.LISTENER_OPTIONS): dict,
                    SchemaOptional(co.STAGER_OPTIONS): dict,
                },
        })

        validation_schema.validate(message_body)

    def _execute(self, message_body: dict) -> dict:
        """
        Custom execution for agent callback processing.
        Deploy agent.
        :param message_body: Received RabbitMQ Message's
        :return: Execution's result
        """
        logger.logger.info("Running AgentTask._execute().", correlation_id=self.correlation_id)

        arguments = message_body.pop(co.ARGUMENTS, {})
        try:
            result = asyncio.run(empire.deploy_agent(arguments))
        except (ConnectionError, EmpireLoginError) as err:
            result = {co.RETURN_CODE: -2, co.OUTPUT: str(err)}

        logger.logger.info("Finished AgentTask._execute().", correlation_id=self.correlation_id)
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
        validation_schema = Schema({
            co.EVENT_T: str,
            co.EVENT_V: Or(
                co.EVENT_VALIDATE_MODULE_SCHEMA, co.EVENT_LIST_MODULES_SCHEMA, co.EVENT_LIST_SESSIONS_SCHEMA,
                co.EVENT_KILL_STEP_EXECUTION_SCHEMA, co.EVENT_HEALTH_CHECK_SCHEMA, co.EVENT_ADD_TRIGGER_HTTP_SCHEMA,
                co.EVENT_ADD_TRIGGER_MSF_SCHEMA, co.EVENT_REMOVE_TRIGGER_SCHEMA, co.EVENT_LIST_TRIGGERS_SCHEMA
            )
        })

        validation_schema.validate(message_body)

    def _execute(self, message_body: dict) -> dict:
        """
        Custom execution for control callback processing.
        Process control event.
        :param message_body: Received RabbitMQ Message's
        :return: Execution's result
        """
        logger.logger.info("Running ControlTask._execute().", correlation_id=self.correlation_id)
        event_t = message_body.pop(co.EVENT_T)
        event_obj = event.Event(message_body.pop(co.EVENT_V), self._main_queue)

        try:  # Get event callable and execute it.
            event_t_lower = event_t.lower()
            event_obj_method = getattr(event_obj, event_t_lower)
        except AttributeError:
            ex = f"Unknown event type: {event_t}."
            event_v = {co.RETURN_CODE: co.CODE_ERROR, co.OUTPUT: ex}
            logger.logger.debug(ex, correlation_id=self.correlation_id)
        else:
            try:
                event_v = event_obj_method()
            except Exception as ex:
                event_v = {co.OUTPUT: {"ex_type": str(ex.__class__), "error": ex.__str__(),
                                       "traceback": traceback.format_exc()}}

        logger.logger.info("Finished ControlTask._execute().", correlation_id=self.correlation_id)
        return {co.EVENT_T: event_t, co.EVENT_V: event_v}

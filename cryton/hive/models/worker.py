from typing import Union, Type
import amqpstorm

from cryton.hive.config.settings import SETTINGS
from cryton.hive.utility import exceptions, states, constants, rabbit_client, logger
from cryton.hive.cryton_app.models import WorkerModel
from cryton.lib.utility.module import Result


class Worker:
    def __init__(self, model_id):
        """
        :param model_id: Model ID
        """
        self.__model = WorkerModel.objects.get(id=model_id)

    @staticmethod
    def create_model(name: str, description: str, force: bool = False) -> WorkerModel:
        """
        Add Worker to DB.
        :param name: Worker's name
        :param description: Worker's description
        :param force: If True, name won't have to be unique
        :return: Added Worker
        """
        if not name:
            raise exceptions.WrongParameterError(message="Parameter cannot be empty", param_name="name")

        elif not force and WorkerModel.objects.filter(name=name).exists():
            raise exceptions.WrongParameterError(
                message="Inserted Worker with such parameter already exists", param_name="name"
            )

        return WorkerModel.objects.create(name=name, description=description)

    def delete(self):
        self.model.delete()

    @property
    def model(self) -> Union[Type[WorkerModel], WorkerModel]:
        self.__model.refresh_from_db()
        return self.__model

    @property
    def name(self) -> str:
        return self.model.name

    @name.setter
    def name(self, value: str):
        model = self.model
        model.name = value
        model.save()

    @property
    def description(self) -> str:
        return self.model.description

    @description.setter
    def description(self, value: str):
        model = self.model
        model.description = value
        model.save()

    @property
    def state(self) -> str:
        return self.model.state

    @state.setter
    def state(self, value: str):
        model = self.model
        model.state = value
        model.save()

    @property
    def attack_q_name(self):
        return f"cryton.worker.{self.name}.attack.request"

    @property
    def control_q_name(self):
        return f"cryton.worker.{self.name}.control.request"

    def healthcheck(self) -> bool:
        """
        Check if Worker is consuming its attack queue
        :return:
        """
        message = {constants.EVENT_T: constants.EVENT_HEALTH_CHECK, constants.EVENT_V: {}}

        with rabbit_client.RpcClient() as rpc_client:
            try:
                response = rpc_client.call(self.control_q_name, message)
                if response.get(constants.EVENT_V).get(constants.RESULT) == Result.OK:
                    self.state = states.UP
                    return True
            except exceptions.RpcTimeoutError:
                pass

            self.state = states.DOWN
            return False

    def prepare_rabbit_queues(self) -> None:
        """
        Declare Rabbit queues in case the Worker is not online yet.
        :return: None
        """
        connection_parameters = {
            "hostname": SETTINGS.rabbit.host,
            "username": SETTINGS.rabbit.username,
            "password": SETTINGS.rabbit.password,
            "port": SETTINGS.rabbit.port,
        }
        with amqpstorm.Connection(**connection_parameters) as connection:
            with connection.channel() as channel:
                channel.queue.declare(self.attack_q_name)

    # TODO: may be easy to use this as a "power feature" to match a session with parameters
    #  session_id: #session{"a": "b"}
    def get_sessions(self, session_filter: dict[str, Union[str, int]]) -> int:
        """
        Get Metasploit Session IDs from Worker.
        :param session_filter: Session parameters to match
        :return: Session ID
        """
        logger.logger.debug("Getting sessions", session_filter=session_filter)
        message = {constants.EVENT_T: constants.EVENT_LIST_SESSIONS, constants.EVENT_V: session_filter}

        with rabbit_client.RpcClient() as rpc_client:
            response = rpc_client.call(self.control_q_name, message)

        return response.get(constants.EVENT_V).get("session_list")

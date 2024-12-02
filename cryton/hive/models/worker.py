from typing import Type
import amqpstorm

from cryton.hive.models.abstract import Instance
from cryton.hive.config.settings import SETTINGS
from cryton.hive.utility import exceptions, states, constants, rabbit_client
from cryton.hive.cryton_app.models import WorkerModel
from cryton.lib.utility.module import Result


class Worker(Instance):
    def __init__(self, model_id: int):
        """
        :param model_id: Model ID
        """
        self.__model = WorkerModel.objects.get(id=model_id)

    @staticmethod
    def create_model(name: str, description: str) -> WorkerModel:
        """
        Add Worker to DB.
        :param name: Worker's name
        :param description: Worker's description
        :return: Added Worker
        """
        return WorkerModel.objects.create(name=name, description=description)

    def delete(self):
        self.model.delete()

    @property
    def model(self) -> WorkerModel | Type[WorkerModel]:
        self.__model.refresh_from_db()
        return self.__model

    @property
    def name(self) -> str:
        return self.model.name

    @property
    def description(self) -> str:
        return self.model.description

    @property
    def state(self) -> str:
        return self.model.state

    @state.setter
    def state(self, value: str):
        model = self.model
        model.state = value
        model.save()

    @property
    def attack_queue(self):
        return f"cryton.worker.{self.name}.attack.request"

    @property
    def control_queue(self):
        return f"cryton.worker.{self.name}.control.request"

    def healthcheck(self) -> bool:
        """
        Check if Worker is consuming its attack queue
        :return:
        """
        message = {constants.EVENT_T: constants.EVENT_HEALTH_CHECK, constants.EVENT_V: {}}

        with rabbit_client.RpcClient() as rpc_client:
            try:
                response = rpc_client.call(self.control_queue, message)
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
        with amqpstorm.Connection(
            SETTINGS.rabbit.host, SETTINGS.rabbit.username, SETTINGS.rabbit.password, SETTINGS.rabbit.port
        ) as connection:
            with connection.channel() as channel:
                channel.queue.declare(self.attack_queue)

from typing import Union, Type
import amqpstorm
from django.core import exceptions as django_exc

from cryton.hive.config.settings import SETTINGS
from cryton.hive.utility import exceptions, states, constants, rabbit_client
from cryton.hive.cryton_app.models import WorkerModel
from cryton.lib.utility.module import Result

class Worker:
    def __init__(self, **kwargs):
        """
        :param kwargs:
            name: str
            description: str
            state: str
        """
        worker_model_id = kwargs.get('worker_model_id')
        if worker_model_id:
            try:
                self.model = WorkerModel.objects.get(id=worker_model_id)
            except django_exc.ObjectDoesNotExist:
                raise exceptions.WorkerObjectDoesNotExist(worker_model_id)

        else:
            self.model = WorkerModel.objects.create(**kwargs)

    def delete(self):
        self.model.delete()

    @property
    def model(self) -> Union[Type[WorkerModel], WorkerModel]:
        self.__model.refresh_from_db()
        return self.__model

    @model.setter
    def model(self, value: WorkerModel):
        self.__model = value

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
    def agent_q_name(self):
        return f"cryton.worker.{self.name}.agent.request"

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
        connection_parameters = {"hostname": SETTINGS.rabbit.host, "username": SETTINGS.rabbit.username,
                                 "password": SETTINGS.rabbit.password, "port": SETTINGS.rabbit.port}
        with amqpstorm.Connection(**connection_parameters) as connection:
            with connection.channel() as channel:
                channel.queue.declare(self.attack_q_name)
                channel.queue.declare(self.agent_q_name)

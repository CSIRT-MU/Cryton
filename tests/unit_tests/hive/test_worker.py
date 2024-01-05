import pytest
from pytest_mock import MockerFixture
from unittest.mock import patch, Mock, call

from cryton.hive.utility import exceptions, logger, constants, states
from cryton.hive.models import worker
from cryton.hive.cryton_app.models import WorkerModel


@patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger(constants.LOGGER_CRYTON_TESTING))
class TestWorker:
    path = "cryton.hive.models.worker"

    @pytest.fixture
    def f_worker_model(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".WorkerModel")

    @pytest.fixture
    def f_worker(self, f_worker_model) -> worker.Worker:
        f_worker_model.objects.create.return_value = Mock()
        return worker.Worker()

    @pytest.fixture
    def f_rpc_client(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".rabbit_client.RpcClient")

    def test_init(self, f_worker_model):
        mock_worker_obj = Mock()
        f_worker_model.objects.create.return_value = mock_worker_obj

        result = worker.Worker(name="test", description="test")

        assert result.model == mock_worker_obj

    def test_init_incorrect_id(self, f_worker_model):
        f_worker_model.objects.get.side_effect = WorkerModel.DoesNotExist()

        with pytest.raises(exceptions.WorkerObjectDoesNotExist):
            worker.Worker(worker_model_id=1)

    def test_delete(self, f_worker):
        f_worker.delete()
        f_worker.model.delete.assert_called_once()

    def test_description(self, f_worker):
        f_worker.description = 'description'
        assert f_worker.description == 'description'

    def test_name(self, f_worker):
        f_worker.name = 'name'
        assert f_worker.name == 'name'

    def test_state(self, f_worker):
        f_worker.state = 'state'
        assert f_worker.state == 'state'

    def test_attack_q_name(self, f_worker):
        f_worker.name = 'test'
        assert f_worker.attack_q_name == "cryton_worker.test.attack.request"

    def test_agent_q_name(self, f_worker):
        f_worker.name = 'test'
        assert f_worker.agent_q_name == "cryton_worker.test.agent.request"

    def test_control_q_name(self, f_worker):
        f_worker.name = 'test'
        assert f_worker.control_q_name == "cryton_worker.test.control.request"

    def test_healthcheck(self, f_worker, f_rpc_client):
        f_rpc_client.return_value.__enter__.return_value.call.return_value = \
            {constants.EVENT_V: {constants.RETURN_CODE: 0}}

        result = f_worker.healthcheck()

        assert result
        assert f_worker.state == states.UP

    def test_healthcheck_fail(self, f_worker, f_rpc_client):
        f_rpc_client.return_value.__enter__.return_value.call.return_value = \
            {constants.EVENT_V: {constants.RETURN_CODE: -1}}

        result = f_worker.healthcheck()

        assert not result
        assert f_worker.state == states.DOWN

    def test_healthcheck_timeout(self, f_worker, f_rpc_client):
        f_rpc_client.return_value.__enter__.return_value.call.side_effect = exceptions.RpcTimeoutError("")

        result = f_worker.healthcheck()

        assert not result
        assert f_worker.state == states.DOWN

    def test_prepare_rabbit_queues(self, f_worker, mocker: MockerFixture):
        f_worker.name = "test"

        mock_channel = Mock()

        mock_connection = mocker.patch(self.path + ".amqpstorm.Connection")
        mock_connection.return_value.__enter__.return_value.channel.return_value.__enter__.return_value = mock_channel

        f_worker.prepare_rabbit_queues()

        mock_channel.queue.declare.assert_has_calls([call(f"cryton_worker.test.attack.request"),
                                                     call(f"cryton_worker.test.agent.request")])

import pytest
from unittest.mock import Mock
from pytest_mock import MockFixture
from cryton.hive.utility import exceptions, logger, constants
from cryton.hive.models import session


@pytest.fixture(autouse=True)
def f_logger(mocker: MockFixture):
    mocker.patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger(constants.LOGGER_CRYTON_TESTING))


class TestSession:
    session_path = "cryton.hive.models.session"
    plan_id = 1
    session_id = "test_id"
    session_name = "test_name"

    @pytest.fixture()
    def f_plan_exec_model(self, mocker: MockFixture):
        return mocker.patch(f"{self.session_path}.PlanExecutionModel")

    @pytest.fixture()
    def f_session_model(self, mocker: MockFixture):
        return mocker.patch(f"{self.session_path}.SessionModel")

    def test_create_session(self, f_plan_exec_model, f_session_model, caplog):
        session_mock = Mock()
        f_session_model.objects.create.return_value = session_mock

        session_object = session.create_session(plan_execution_id=self.plan_id,
                                                session_id=self.session_id,
                                                session_name=self.session_name)

        f_plan_exec_model.objects.filter.assert_called_once_with(id=self.plan_id)
        f_session_model.objects.create.assert_called_once_with(plan_execution_id=self.plan_id,
                                                               name=self.session_name,
                                                               msf_id=self.session_id)

        assert session_object == session_mock
        assert "Creating named session" in caplog.text
        assert "Named session created" in caplog.text

    def test_create_session_exception(self, f_plan_exec_model, caplog):
        with pytest.raises(exceptions.PlanExecutionDoesNotExist):
            f_plan_exec_model.objects.filter.return_value.exists.return_value = False
            session.create_session(plan_execution_id=self.plan_id,
                                   session_id=self.session_id,
                                   session_name=self.session_name)

        assert "Creating named session" in caplog.text

    def test_get_msf_session_id(self, f_session_model, caplog):
        session_mock = Mock(msf_id=self.session_id)
        f_session_model.objects.get.return_value = session_mock

        session_id = session.get_msf_session_id(session_name=self.session_name, plan_execution_id=self.plan_id)

        f_session_model.objects.get.assert_called_once_with(name=self.session_name,
                                                            plan_execution_id=self.plan_id)

        assert session_id == self.session_id
        assert "Getting session id" in caplog.text

    def test_get_msf_session_id_exception(self, f_session_model):
        f_session_model.objects.get.side_effect = session.ObjectDoesNotExist

        with pytest.raises(exceptions.SessionObjectDoesNotExist):
            session.get_msf_session_id('non-existent-session', self.plan_id)


# TODO: update along with a fix of get_session_ids method
    # def test_get_session_ids(self, ):
    #     mock_stub = Mock()
    #     mock_stub.sessions_list().sess_list = '["1", "2"]'
    #
    #     self.step_model.use_any_session_to_target = '1.2.3.4'
    #     session_list = session.get_session_ids('1.2.3.4', self.plan_exec_obj.id)
    #
    #     self.assertEqual('2', session_list[-1])

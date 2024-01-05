import pytest
from pytest_mock import MockerFixture
from unittest.mock import patch, Mock

from cryton.hive.utility import logger, states, constants, event, exceptions


@patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger(constants.LOGGER_CRYTON_TESTING))
class TestEvent:
    path = "cryton.hive.utility.event"

    @pytest.fixture
    def f_step_execution(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".step.StepExecution")

    @pytest.fixture
    def f_stage_execution_model(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".stage.StageExecutionModel")

    @pytest.fixture
    def f_stage_execution(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".stage.StageExecution")

    @pytest.fixture
    def f_plan_execution(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".plan.PlanExecution")

    @pytest.fixture
    def f_run(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".run.Run")

    @pytest.fixture
    def f_scheduler_service(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".SchedulerService")

    @pytest.fixture
    def f_create_session(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".session.create_session")

    @pytest.fixture
    def f_stage_state_machine(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".states.StageStateMachine")

    def test_trigger_stage_http(self, f_stage_execution, f_stage_execution_model, f_create_session,
                                f_stage_state_machine):
        stage_ex_mock = Mock()
        stage_ex_mock.model.stage_model.trigger_type = constants.HTTP_LISTENER
        stage_ex_mock.state = states.AWAITING

        f_stage_execution_model.objects.get.return_value.id = 1
        f_stage_execution.return_value = stage_ex_mock

        event.Event({constants.TRIGGER_ID: "id"}).trigger_stage()

        stage_ex_mock.trigger.stop.assert_called_once()
        stage_ex_mock.execute.assert_called_once()
        f_create_session.assert_not_called()

    def test_trigger_stage_msf(self, f_stage_execution, f_stage_execution_model, f_create_session,
                               f_stage_state_machine):
        stage_ex_mock = Mock()
        stage_ex_mock.model.stage_model.trigger_type = constants.MSF_LISTENER
        stage_ex_mock.state = states.AWAITING
        stage_ex_mock.model.stage_model.name = "test"
        stage_ex_mock.model.plan_execution_id = 1

        f_stage_execution_model.objects.get.return_value.id = 1
        f_stage_execution.return_value = stage_ex_mock

        event.Event({constants.TRIGGER_ID: "id"}).trigger_stage()

        stage_ex_mock.trigger.stop.assert_called_once()
        f_create_session.assert_called_once_with(1, None, "test_session")
        stage_ex_mock.execute.assert_called_once()

    def test_trigger_stage_incorrect_state(self, f_stage_execution, f_stage_execution_model, f_create_session,
                                           f_stage_state_machine):
        stage_ex_mock = Mock()
        stage_ex_mock.model.stage_model.trigger_type = constants.MSF_LISTENER
        stage_ex_mock.state = states.RUNNING

        f_stage_execution_model.objects.get.return_value.id = 1
        f_stage_execution.return_value = stage_ex_mock

        f_stage_state_machine.side_effect = exceptions.StageInvalidStateError("", 1, "", [])

        with pytest.raises(exceptions.StageInvalidStateError):
            event.Event({constants.TRIGGER_ID: "id"}).trigger_stage()

    def test_handle_finished_step(self, f_step_execution, f_stage_execution, f_plan_execution, f_run):
        f_stage_execution.return_value.all_steps_finished = True
        f_plan_execution.return_value.all_stages_finished = True
        f_run.return_value.all_plans_finished = True

        event.Event({"step_execution_id": 1}).handle_finished_step()

        f_stage_execution.return_value.finish.assert_called_once()
        f_plan_execution.return_value.finish.assert_called_once()
        f_run.return_value.finish.assert_called_once()

    def test_handle_finished_step_dynamic_plan(self, f_step_execution, f_stage_execution, f_plan_execution, f_run):
        f_stage_execution.return_value.all_steps_finished = True
        f_stage_execution.return_value.model.stage_model.plan_model.dynamic = True
        f_stage_execution.return_value.state = states.FINISHED

        event.Event({"step_execution_id": 1}).handle_finished_step()

        f_stage_execution.return_value.finish.assert_not_called()
        f_plan_execution.return_value.finish.assert_not_called()
        f_run.return_value.finish.assert_not_called()

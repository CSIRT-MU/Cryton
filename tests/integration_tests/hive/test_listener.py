from django.test import TestCase
from model_bakery import baker

from unittest.mock import patch, Mock
import json
import yaml
import os
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from cryton_core.lib.services import listener
from cryton_core.lib.util import creator, logger, states
from cryton_core.lib.models import stage, plan, step, run, worker

from cryton_core.cryton_app.models import WorkerModel, PlanModel, RunModel, CorrelationEventModel

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


@patch('cryton_core.lib.util.logger.logger', logger.structlog.getLogger('cryton-core-test'))
@patch('cryton_core.lib.services.listener.Process', Mock())
@patch('cryton_core.lib.services.listener.Event', Mock())
@patch('amqpstorm.Connection', Mock())
@patch('amqpstorm.Message', Mock())
class TestListener(TestCase):

    def setUp(self):
        mock_db = patch('cryton_core.lib.services.scheduler.SQLAlchemyJobStore',
                        return_value=SQLAlchemyJobStore('sqlite:///jobs.sqlite'))
        mock_db.start()
        self.stage_execution = baker.make(stage.StageExecutionModel)
        self.step_model = baker.make(step.StepModel)
        self.step_execution_obj = step.StepExecutionModel.objects.create(step_model=self.step_model,
                                                                         stage_execution=self.stage_execution)

        self.properties = dict()
        self.properties["correlation_id"] = CorrelationEventModel.objects.create(
            correlation_id='test_corr_id', step_execution_id=self.step_execution_obj.id).correlation_id
        self.listener_obj = listener.Listener()
        self.listener_obj._scheduler = Mock()

    def tearDown(self) -> None:
        self.listener_obj.stop()

    def test_event_callback_pause(self):
        plan_obj = baker.make(PlanModel)
        worker_obj = baker.make(WorkerModel, name="test")
        run_obj = baker.make(RunModel, state=states.PAUSING)

        plan_execution_obj = plan.PlanExecution(plan_model=plan_obj, worker=worker_obj, run=run_obj,
                                                state=states.PAUSING)

        body = dict(event_t='PAUSE', event_v=dict(result='OK', plan_execution_id=plan_execution_obj.model.id))
        message = Mock()
        message.body = json.dumps(body)
        self.listener_obj.event_callback(message)

    def test_event_callback_nonexistent(self):
        body = dict(event_t='Nonexistent_event', event_v=dict(result='wut'))
        message = Mock()
        message.body = json.dumps(body)
        with self.assertLogs('cryton-core-test', level='WARN') as cm:
            self.listener_obj.event_callback(message)

        for log in cm.output:
            if "Nonexistent event received" in log:
                break
        else:
            raise AssertionError("String not found in any log message")

    # def test_control_callback(self):
    #     body = dict(control_t='VALIDATE_MODULES', control_v=dict(result='OK'))
    #     message = Mock()
    #     message.body = json.dumps(body)
    #     message.properties = self.properties
    #     message.correlation_id = self.properties.get('correlation_id')
    #     self.listener_obj.control_resp_callback(message)
    #
    # def test_control_callback_nonexistent(self):
    #     body = dict(control_t='Nonexistent_control_event', control_v=dict(result='wut'))
    #     message = Mock()
    #     message.body = json.dumps(body)
    #     message.properties = self.properties
    #     message.correlation_id = self.properties.get('correlation_id')
    #     with self.assertLogs('cryton-core-test', level='WARN') as cm:
    #         self.listener_obj.control_resp_callback(message)
    #
    #     self.assertIn("Nonexistent control event received", cm.output[0])

    def test_step_resp_callback(self):
        with open(TESTS_DIR + '/plan.yaml') as plan_yaml:
            plan_dict = yaml.safe_load(plan_yaml)

        worker_obj = baker.make(WorkerModel, name="test")
        plan_obj_id = creator.create_plan(plan_dict)
        run_obj = run.Run(plan_model_id=plan_obj_id, workers=[worker_obj])

        plan_exec_obj = plan.PlanExecution(
            plan_execution_id=plan.PlanExecutionModel.objects.get(run_id=run_obj.model.id).id)
        stage_exec_obj = stage.StageExecution(stage_execution_id=plan_exec_obj.model.stage_executions.all()[0].id)
        step_exec_obj_1 = step.StepExecution(step_execution_id=stage_exec_obj.model.step_executions.all()[0].id)
        step_exec_obj_2 = step.StepExecution(step_execution_id=stage_exec_obj.model.step_executions.all()[1].id)

        properties = dict()
        properties["correlation_id"] = CorrelationEventModel.objects.create(
            correlation_id='unique_test_corr_id_1', step_execution_id=step_exec_obj_1.model.id).correlation_id

        step_exec_obj_1.state = states.STARTING
        step_exec_obj_1.state = states.RUNNING
        step_exec_obj_2.state = states.PENDING
        stage_exec_obj.state = states.SCHEDULED
        stage_exec_obj.state = states.RUNNING
        plan_exec_obj.state = states.RUNNING
        run_obj.state = states.RUNNING

        body = dict(serialized_output='test', output='test')
        message = Mock()
        message.body = json.dumps(body)
        message.properties = properties
        message.correlation_id = properties.get('correlation_id')

        with self.assertLogs('cryton-core-test', level='INFO') as cm:
            self.listener_obj.step_response_callback(message)

        self.assertIn("Step execution finished", cm.output[0])

        self.assertEqual(step_exec_obj_1.state, states.FINISHED)
        self.assertEqual(step_exec_obj_2.state, states.IGNORED)
        self.assertEqual(stage_exec_obj.state, states.FINISHED)
        self.assertEqual(plan_exec_obj.state, states.FINISHED)

        self.assertEqual(run_obj.all_plans_finished, True)
        self.assertEqual(run_obj.state, states.FINISHED)

    @patch('cryton_core.lib.util.rabbit_client.RpcClient.__enter__')
    def test_worker_healthcheck(self, mock_rpc):
        worker_tmp_id = creator.create_worker('test', 'desc')
        worker_tmp = worker.Worker(worker_model_id=worker_tmp_id)

        mock_call = Mock()
        mock_call.call = Mock(return_value={'event_v': {'return_code': 0}})
        mock_rpc.return_value = mock_call
        worker_tmp.healthcheck()

        self.assertEqual(worker_tmp.state, states.UP)

    def test_get_correlation_id(self):
        correlation_obj = CorrelationEventModel.objects.create(
            correlation_id='unique_test_corr_id_1', step_execution_id=self.step_execution_obj.id)

        resp = self.listener_obj._get_correlation_event(correlation_obj.correlation_id)
        self.assertEqual(resp, correlation_obj)

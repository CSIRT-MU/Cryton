# from django.test import TestCase
# from model_bakery import baker
# import datetime
# import os
# import yaml
# from unittest.mock import patch, Mock, MagicMock
#
# from cryton.hive.utility import creator, exceptions, logger, states
# from cryton.hive.models import step, run, plan, worker
#
# from cryton.hive.cryton_app.models import PlanModel, WorkerModel, StepExecutionModel
# from django.utils import timezone
#
#
# TESTS_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger('cryton-core-test'))
# @patch("cryton.hive.models.plan.os.makedirs", Mock())
# class TestRun(TestCase):
#
#     def setUp(self) -> None:
#         self.plan_obj = baker.make(PlanModel)
#
#         self.worker_1 = baker.make(WorkerModel, **{'name': 'test_worker_name1', 'description': 'test_description_1'})
#         self.worker_2 = baker.make(WorkerModel, **{'name': 'test_worker_name2', 'description': 'test_description_2'})
#         self.worker_3 = baker.make(WorkerModel, **{'name': 'test_worker_name3', 'description': 'test_description_3'})
#
#         self.workers = [self.worker_1, self.worker_2, self.worker_3]
#         self.workers_id_list = [self.worker_1.id, self.worker_2.id, self.worker_3.id]
#         self.run_obj = run.Run(plan_model_id=self.plan_obj.id, workers=self.workers)
#
#     @patch('cryton.hive.utility.scheduler_client.schedule_function', Mock(return_value=1))
#     @patch('cryton.hive.utility.scheduler_client.remove_job', Mock(return_value=1))
#     def test_schedule(self):
#         self.assertEqual(self.run_obj.state, states.PENDING)
#
#         with self.assertRaises(exceptions.RunInvalidStateError):
#             self.run_obj.reschedule(timezone.now())
#
#         schedule_time_dt = timezone.now()
#         self.run_obj.schedule(schedule_time_dt)
#
#         self.assertEqual(self.run_obj.state, states.SCHEDULED)
#         self.assertEqual(self.run_obj.schedule_time, schedule_time_dt)
#
#         self.run_obj.reschedule(timezone.now() + datetime.timedelta(minutes=5))
#         self.assertEqual(self.run_obj.state, states.SCHEDULED)
#
#         self.run_obj.unschedule()
#         self.assertEqual(self.run_obj.state, states.PENDING)
#         self.assertIsNone(self.run_obj.schedule_time)
#
#         self.run_obj.state = states.RUNNING
#         for pex in self.run_obj.model.plan_executions.all():
#             pex.state = states.RUNNING
#             pex.save()
#
#         self.run_obj.pause()
#
#         self.assertEqual(self.run_obj.state, states.PAUSED)
#
#
#     @patch('cryton.hive.utility.scheduler_client.schedule_function')
#     @patch('cryton.hive.utility.scheduler_client.remove_job')
#     @patch("amqpstorm.Connection", MagicMock())
#     def test_execute(self, mock_remove, mock_sched):
#         mock_sched.return_value = 0
#         mock_remove.return_value = 0
#         with open(TESTS_DIR + '/plan.yaml') as plan_yaml:
#             plan_dict = yaml.safe_load(plan_yaml)
#
#         plan_obj_id = creator.create_plan(plan_dict)
#         run_obj = run.Run(plan_model_id=plan_obj_id, workers=self.workers)
#
#         run_obj.execute()
#
#         self.assertEqual(run_obj.state, states.RUNNING)
#         for exec_obj in run_obj.model.plan_executions.filter(worker_id__in=self.workers_id_list):
#             self.assertEqual(exec_obj.state, states.RUNNING)
#
#         run_obj.pause()
#         for exec_obj in run_obj.model.plan_executions.filter(worker_id__in=self.workers_id_list):
#             self.assertEqual(exec_obj.state, states.PAUSED)
#
#         # this is a replacement for __change_conditional_state cause threading and django don't work well in tests
#         for exec_obj in run_obj.model.plan_executions.all():
#             plan.PlanExecution(plan_execution_id=exec_obj.id).state = states.PAUSED
#
#         run_obj.resume()
#         for exec_obj in run_obj.model.plan_executions.filter(worker_id__in=self.workers_id_list):
#             self.assertEqual(exec_obj.state, states.RUNNING)
#
#     @patch('cryton.hive.utility.scheduler_client.schedule_function')
#     def test_plan_run(self, mock_sched):
#         mock_sched.return_value = 0
#         with open(TESTS_DIR + '/plan.yaml') as plan_yaml:
#             plan_dict = yaml.safe_load(plan_yaml)
#
#         plan_obj_id = creator.create_plan(plan_dict)
#         run_obj = run.Run(plan_model_id=plan_obj_id, workers=self.workers)
#
#         run_obj.schedule(timezone.now())
#
#         self.assertEqual(run_obj.state, states.SCHEDULED)
#
#     def test_with_rabbit(self):
#         with open(TESTS_DIR + '/complicated-test-plan.yaml') as plan_yaml:
#             plan_dict = yaml.safe_load(plan_yaml)
#
#         plan_obj_id = creator.create_plan(plan_dict)
#         worker_obj_id = creator.create_worker('test', '1.2.3.4')
#         worker_obj = worker.Worker(worker_model_id=worker_obj_id)
#
#         run.Run(plan_model_id=plan_obj_id, workers=[worker_obj.model])
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger('cryton-core-test'))
# @patch("cryton.hive.models.plan.os.makedirs", Mock())
# class TestVariables(TestCase):
#
#     def setUp(self) -> None:
#         self.worker_model_1 = baker.make(WorkerModel, **{'name': 'test_worker_name1', 'description': 'test_description_1'})
#         self.worker_instance_1 = worker.Worker(worker_model_id=self.worker_model_1.id)
#         self.workers = [self.worker_model_1]
#         pass
#
#     @patch('cryton.hive.utility.scheduler_client.schedule_function')
#     @patch('cryton.hive.utility.scheduler_client.remove_job')
#     @patch('cryton.hive.models.step.StepExecutionWorkerExecute.execute')
#     def test_use_var(self,  mock_exec, mock_remove, mock_sched):
#         mock_sched.return_value = 0
#         mock_remove.return_value = 0
#         with open(TESTS_DIR + '/plan-vars.yaml') as plan_yaml:
#             plan_dict = yaml.safe_load(plan_yaml)
#
#         plan_obj_id = creator.create_plan(plan_dict)
#         run_obj = run.Run(plan_model_id=plan_obj_id, workers=self.workers)
#
#         # Get StepExecutions
#         step_ex_obj = step.StepExecutionWorkerExecute(step_execution_id=StepExecutionModel.objects.get(
#             stage_execution__plan_execution__run=run_obj.model,
#             step_model__name='step1').id)
#
#         output = {'serialized_output': {'cmd_output': 'testing'}}
#         step_ex_obj.save_output(output)
#
#         step_ex_obj_2 = StepExecutionModel.objects.get(stage_execution__plan_execution__run=run_obj.model,
#                                                        step_model__name='step2')
#
#         rabbit_channel = MagicMock()
#         step_ex = step.StepExecutionWorkerExecute(step_execution_id=step_ex_obj_2.id)
#         step_ex.execute(rabbit_channel=rabbit_channel)
#
#         mock_exec.assert_called_with(rabbit_channel=rabbit_channel)
#
#     @patch('cryton.hive.utility.scheduler_client.schedule_function')
#     @patch('cryton.hive.utility.scheduler_client.remove_job')
#     @patch('cryton.hive.models.step.StepExecutionWorkerExecute.execute')
#     def test_use_var_prefix(self, mock_exec, mock_remove, mock_sched):
#         mock_sched.return_value = 0
#         mock_remove.return_value = 0
#         with open(TESTS_DIR + '/plan-vars-prefix.yaml') as plan_yaml:
#             plan_dict = yaml.safe_load(plan_yaml)
#
#         plan_obj_id = creator.create_plan(plan_dict)
#         run_obj = run.Run(plan_model_id=plan_obj_id, workers=self.workers)
#
#         # Get StepExecutions
#         step_ex_obj = step.StepExecutionWorkerExecute(step_execution_id=StepExecutionModel.objects.get(
#             stage_execution__plan_execution__run=run_obj.model,
#             step_model__name='step1').id)
#
#         output = {'serialized_output': {'cmd_output': 'testing'}}
#         step_ex_obj.save_output(output)
#
#         step_ex_obj_2 = StepExecutionModel.objects.get(stage_execution__plan_execution__run=run_obj.model,
#                                                        step_model__name='step2')
#
#         rabbit_channel = MagicMock()
#         step_ex = step.StepExecutionWorkerExecute(step_execution_id=step_ex_obj_2.id)
#         step_ex.execute(rabbit_channel=rabbit_channel)
#
#         mock_exec.assert_called_with(rabbit_channel=rabbit_channel)
#
#
#     @patch('cryton.hive.utility.scheduler_client.schedule_function')
#     @patch('cryton.hive.utility.scheduler_client.remove_job')
#     @patch('cryton.hive.models.step.StepExecutionWorkerExecute.execute')
#     def test_use_var_mapping(self, mock_exec, mock_remove, mock_sched):
#         mock_sched.return_value = 0
#         mock_remove.return_value = 0
#         with open(TESTS_DIR + '/plan-vars-mapping.yaml') as plan_yaml:
#             plan_dict = yaml.safe_load(plan_yaml)
#
#         plan_obj_id = creator.create_plan(plan_dict)
#         run_obj = run.Run(plan_model_id=plan_obj_id, workers=self.workers)
#
#         # Get StepExecutions
#         step_ex_obj = step.StepExecutionWorkerExecute(step_execution_id=StepExecutionModel.objects.get(
#             stage_execution__plan_execution__run=run_obj.model,
#             step_model__name='step1').id)
#
#         output = {'serialized_output': {'cmd_output': 'testing'}}
#         step_ex_obj.save_output(output)
#
#         step_ex_obj_2 = StepExecutionModel.objects.get(stage_execution__plan_execution__run=run_obj.model,
#                                                        step_model__name='step2')
#
#         rabbit_channel = MagicMock()
#         step_ex = step.StepExecutionWorkerExecute(step_execution_id=step_ex_obj_2.id)
#         step_ex.execute(rabbit_channel=rabbit_channel)
#
#         mock_exec.assert_called_with(rabbit_channel=rabbit_channel)
#
#     @patch('cryton.hive.utility.scheduler_client.schedule_function')
#     @patch('cryton.hive.utility.scheduler_client.remove_job')
#     @patch('cryton.hive.models.step.StepExecutionWorkerExecute.execute')
#     def test_use_var_parent(self, mock_exec, mock_remove, mock_sched):
#         mock_sched.return_value = 0
#         mock_remove.return_value = 0
#         with open(TESTS_DIR + '/plan-vars-parent.yaml') as plan_yaml:
#             plan_dict = yaml.safe_load(plan_yaml)
#
#         plan_obj_id = creator.create_plan(plan_dict)
#         run_obj = run.Run(plan_model_id=plan_obj_id, workers=self.workers)
#
#         # Get StepExecutions
#         step_ex_obj = step.StepExecutionWorkerExecute(step_execution_id=StepExecutionModel.objects.get(
#             stage_execution__plan_execution__run=run_obj.model,
#             step_model__name='step1').id)
#
#         output = {'output': None, 'serialized_output': {'cmd_output': 'testing'}}
#         step_ex_obj.save_output(output)
#
#         step_ex_obj_2 = StepExecutionModel.objects.get(stage_execution__plan_execution__run=run_obj.model,
#                                                        step_model__name='step2')
#
#         rabbit_channel = MagicMock()
#         succ_step_ex_obj = step.StepExecutionWorkerExecute(step_execution_id=step_ex_obj_2.id)
#         succ_step_ex_obj.parent_id = step_ex_obj.model.id
#         succ_step_ex_obj.execute(rabbit_channel=rabbit_channel)
#
#         mock_exec.assert_called_with(rabbit_channel=rabbit_channel)

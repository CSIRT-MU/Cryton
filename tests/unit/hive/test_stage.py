# from django.test import TestCase
# from unittest.mock import patch, MagicMock, Mock
# from cryton.hive.utility import creator, exceptions, logger
# from cryton.hive.models import stage
#
# from cryton.hive.triggers import trigger_delta
#
# import yaml
# import os
# from model_bakery import baker
#
# from cryton.hive.cryton_app.models import PlanModel, StageModel, StepModel, StepExecutionModel, StageExecutionModel, \
#     PlanExecutionModel, DependencyModel
#
# from django.utils import timezone
#
# TESTS_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger('cryton-core-debug'))
# class TestStage(TestCase):
#
#     def setUp(self) -> None:
#         self.plan_model = baker.make(PlanModel)
#         self.stage_args = {'plan_model_id': self.plan_model.id,
#                            'name': 'stage',
#                            'trigger_type': "test",
#                            'trigger_args': {}
#                            }
#         self.stage_validation_args = {'name': 'stage',
#                                       'trigger_type': "",
#                                       'trigger_args': {},
#                                       'steps': [{'name': 'test step', 'is_init': True}]
#                                       }
#         self.stage_obj = stage.Stage(**self.stage_args)
#
#     def test_init(self):
#         stage_obj = stage.Stage(**self.stage_args)
#
#         self.assertIsInstance(stage_obj.model.id, int)
#
#     def test_init_from_file(self):
#         f_in = open('{}/stage.yaml'.format(TESTS_DIR))
#         stage_yaml = yaml.safe_load(f_in)
#         stage_yaml.update({'plan_model_id': self.plan_model.id})
#         del stage_yaml['steps']
#         stage_obj = stage.Stage(**stage_yaml)
#
#         self.assertIsInstance(stage_obj.model.id, int)
#
#     def test_delete(self):
#         stage_obj = stage.Stage(**self.stage_args)
#
#         stage_id = stage_obj.model.id
#         stage_obj.delete()
#         with self.assertRaises(exceptions.StageObjectDoesNotExist):
#             stage.Stage(stage_model_id=stage_id)
#
#     def test_property_model(self):
#         self.stage_obj.model.plan_model_id = self.plan_model.id
#         self.assertEqual(self.stage_obj.model.plan_model_id, self.plan_model.id)
#
#     def test_property_name(self):
#         self.stage_obj.name = 'test'
#         self.assertEqual(self.stage_obj.name, 'test')
#
#     def test_property_executor(self):
#         self.stage_obj.executor = 'test'
#         self.assertEqual(self.stage_obj.executor, 'test')
#
#     def test_property_trigger_type(self):
#         self.stage_obj.trigger_type = 'test'
#         self.assertEqual(self.stage_obj.trigger_type, 'test')
#
#     def test_property_trigger_args(self):
#         self.stage_obj.trigger_args = {'test': 'test'}
#         self.assertEqual(self.stage_obj.trigger_args, {'test': 'test'})
#
#     def test_property_final_steps(self):
#         step_args = {'stage_model_id': self.stage_obj.model.id,
#                      'is_init': False,
#                      'is_final': True,
#                      'arguments': {},
#                      'name': 'final_step'}
#         StepModel.objects.create(**step_args)
#         step_args.update({'is_final': False, 'name': 'not_final_step'})
#         StepModel.objects.create(**step_args)
#         self.assertEqual(len(self.stage_obj.final_steps), 1)
#         self.assertEqual(self.stage_obj.final_steps[0].name, 'final_step')
#
#     def test_property_execution_list(self):
#         self.assertIsInstance(self.stage_obj.execution_list, stage.QuerySet)
#
#     def test_filter_without_param(self):
#         stage_model1 = baker.make(StageModel, name="test1")
#         stage_model2 = baker.make(StageModel, name="test2")
#         ret = stage.Stage.filter()
#
#         self.assertTrue(stage_model1 in ret and stage_model2 in ret)
#
#     def test_filter_with_correct_param(self):
#         stage_model1 = baker.make(StageModel, name="test1")
#         stage_model2 = baker.make(StageModel, name="test2")
#         ret = stage.Stage.filter(name='test1')
#
#         self.assertTrue(stage_model1 in ret and stage_model2 not in ret)
#
#     def test_filter_with_incorrect_param(self):
#         with self.assertRaises(exceptions.WrongParameterError):
#             stage.Stage.filter(incorrect='test1')
#
#     @patch('cryton.hive.models.step.Step.validate', MagicMock)
#     def test_validate_incorrect_stage_dict(self):
#         stage_dict = self.stage_validation_args
#         stage_dict.update({'trigger_type': 'delta'})
#
#         with self.assertRaises(exceptions.StageValidationError):
#             stage.Stage.validate(stage_dict)
#
#     @patch('cryton.hive.models.step.Step.validate', MagicMock)
#     def test_validate_delta_correct_dict(self):
#         stage_dict = self.stage_validation_args
#         stage_dict.update({'trigger_type': 'delta'})
#         stage_dict.update({'trigger_args': {'hours': 0, 'minutes': 10}})
#
#         self.assertTrue(stage.Stage.validate(stage_dict))
#
#     @patch('cryton.hive.models.step.Step.validate', MagicMock)
#     def test_validate_delta_no_dict(self):
#         stage_dict = self.stage_validation_args
#         stage_dict.update({'trigger_type': 'delta'})
#
#         with self.assertRaises(exceptions.StageValidationError):
#             (stage.Stage.validate(stage_dict))
#
#     @patch('cryton.hive.models.step.Step.validate', MagicMock)
#     def test_validate_unknown_trigger(self):
#         stage_dict = self.stage_validation_args
#         stage_dict.update({'trigger_type': 'unknown'})
#
#         with self.assertRaises(exceptions.StageValidationError):
#             (stage.Stage.validate(stage_dict))
#
#     @patch('cryton.hive.models.step.Step.validate', MagicMock)
#     def test_validate_no_steps(self):
#         stage_dict = self.stage_validation_args
#         stage_dict.update({'trigger_type': 'delta'})
#         stage_dict.update({'trigger_args': {'minutes': 10}})
#         stage_dict.update({'steps': []})
#
#         with self.assertRaises(exceptions.StageValidationError):
#             stage.Stage.validate(stage_dict)
#
#     @patch('cryton.hive.models.step.Step.validate', MagicMock)
#     def test_validate_HTTPListener_correct_dict(self):
#         stage_dict = self.stage_validation_args
#         arg_dict = {'host': '127.0.0.1',
#                     'port': 0,
#                     'routes': [
#                         {
#                             'path': '/',
#                             'method': 'test',
#                             'parameters': [
#                                 {'name': 'name',
#                                  'value': 'value'
#                                  }
#                             ]
#                         }
#                     ]
#                     }
#         stage_dict.update({'trigger_type': 'HTTPListener'})
#         stage_dict.update({'trigger_args': arg_dict})
#
#         self.assertTrue(stage.Stage.validate(stage_dict))
#
#     @patch('cryton.hive.models.step.Step.validate', MagicMock)
#     def test_validate_HTTPListener_incorrect_dict(self):
#         stage_dict = self.stage_validation_args
#         stage_dict.update({'trigger_type': 'HTTPListener'})
#
#         with self.assertRaises(exceptions.StageValidationError):
#             stage.Stage.validate(stage_dict)
#
#     @patch('cryton.hive.models.step.Step.validate', MagicMock)
#     def test_validate_successor_as_init_invalid(self):
#         stage_dict = self.stage_validation_args
#         stage_dict.update({'trigger_type': 'delta'})
#         stage_dict.update({'trigger_args': {'minutes': 10}})
#         stage_dict["steps"].append({"name": "step 1", "is_init": True, "next": [{"step": "step 2"}]})
#         stage_dict["steps"].append({"name": "step 2", "is_init": True})
#
#         with self.assertRaises(exceptions.StageValidationError):
#             stage.Stage.validate(stage_dict)
#
#     @patch('cryton.hive.models.step.Step.validate', MagicMock)
#     def test_validate_successor_as_init_valid(self):
#         stage_dict = self.stage_validation_args
#         stage_dict.update({'trigger_type': 'delta'})
#         stage_dict.update({'trigger_args': {'minutes': 10}})
#         stage_dict["steps"].append({"name": "step 1", "is_init": True, "next": [{"step": "step 2"}]})
#         stage_dict["steps"].append({"name": "step 2", "is_init": False})
#
#         stage.Stage.validate(stage_dict)
#
#     def test_dfs(self):
#         graph = {'1': {'2', '3'}, '2': set(), '4': {'2'}, '3': {'1'}}
#         with self.assertRaises(exceptions.StageCycleDetected):
#             stage.Stage._dfs_reachable(set(), set(), graph, '1')
#
#         graph = {'1': {'2', '3'}, '2': {'4'}, '4': {'5'}, '5': set()}
#         reachable = stage.Stage._dfs_reachable(set(), set(), graph, '1')
#         self.assertEqual({'1', '2', '3', '4', '5'}, reachable)
#
#         graph = {'1': {'2', '3'}, '2': {'4'}, '4': set(), '5': set()}
#         reachable = stage.Stage._dfs_reachable(set(), set(), graph, '1')
#         self.assertEqual({'1', '2', '3', '4'}, reachable)
#
#     def test_add_dependency(self):
#         dependency = baker.make(StageModel)
#         new_dependency_id = self.stage_obj.add_dependency(dependency.id)
#         dependency_instance = DependencyModel.objects.get(id=new_dependency_id)
#         self.assertEqual(self.stage_obj.model.id, dependency_instance.stage_model_id)
#         self.assertEqual(dependency.id, dependency_instance.dependency_id)
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger('cryton-core-debug'))
# @patch('cryton.hive.utility.states.StageStateMachine.validate_transition', MagicMock())
# @patch('cryton.hive.utility.states.StageStateMachine.validate_state', MagicMock())
# class TestStageExecute(TestCase):
#
#     def setUp(self) -> None:
#         self.plan_model = baker.make(PlanModel)
#         self.plan_ex_model = baker.make(PlanExecutionModel, **{'start_time': timezone.now()})
#         self.stage_model = baker.make(
#             StageModel, **{'trigger_type': 'delta', 'trigger_args': {'minutes': 10}}
#         )
#         self.stage_ex_stats = {
#             'stage_model': self.stage_model,
#             'plan_execution': self.plan_ex_model
#         }
#         self.stage_ex_model = baker.make(StageExecutionModel, **self.stage_ex_stats)
#         self.stage_ex_obj = stage.StageExecution(**self.stage_ex_stats)
#
#     def test_init(self):
#         stage_ex = StageExecutionModel.objects.create(**self.stage_ex_stats)
#
#         self.assertIsInstance(stage_ex.id, int)
#
#     def test_init_existing(self):
#         stage_ex = stage.StageExecution(stage_execution_id=self.stage_ex_obj.model.id)
#
#         self.assertIsInstance(stage_ex.model.id, int)
#
#     def test_delete(self):
#         stage_ex_id = self.stage_ex_obj.model.id
#         self.stage_ex_obj.delete()
#         with self.assertRaises(exceptions.StageExecutionObjectDoesNotExist):
#             stage.StageExecution(stage_execution_id=stage_ex_id)
#
#     def test_property_model(self):
#         self.stage_ex_obj.model.plan_execution = self.plan_ex_model
#         self.assertEqual(self.stage_ex_obj.model.plan_execution_id, self.plan_ex_model.id)
#
#     def test_property_state(self):
#         self.stage_ex_obj.state = 'RUNNING'
#         self.assertEqual(self.stage_ex_obj.state, 'RUNNING')
#
#     def test_property_aps_job_id(self):
#         self.stage_ex_obj.aps_job_id = 'test'
#         self.assertEqual(self.stage_ex_obj.aps_job_id, 'test')
#
#     def test_property_logbook_uuid(self):
#         self.stage_ex_obj.logbook_uuid = 'test'
#         self.assertEqual(self.stage_ex_obj.logbook_uuid, 'test')
#
#     def test_property_start_time(self):
#         test_time = timezone.now()
#         self.stage_ex_obj.start_time = test_time
#
#         self.assertEqual(self.stage_ex_obj.start_time, test_time)
#
#     def test_property_pause_time(self):
#         test_time = timezone.now()
#         self.stage_ex_obj.pause_time = test_time
#
#         self.assertEqual(self.stage_ex_obj.pause_time, test_time)
#
#     def test_property_finish_time(self):
#         test_time = timezone.now()
#         self.stage_ex_obj.finish_time = test_time
#
#         self.assertEqual(self.stage_ex_obj.finish_time, test_time)
#
#     def test_property_trigger_id(self):
#         test_trigger_id = "test_id"
#         self.stage_ex_obj.trigger_id = test_trigger_id
#
#         self.assertEqual(self.stage_ex_obj.trigger_id, test_trigger_id)
#
#     def test_filter_without_param(self):
#         stage_ex_model1 = baker.make(StageExecutionModel, state="test1")
#         stage_ex_model2 = baker.make(StageExecutionModel, state="test2")
#         ret = stage.StageExecution.filter()
#
#         self.assertTrue(stage_ex_model1 in ret and stage_ex_model2 in ret)
#
#     def test_filter_with_correct_param(self):
#         stage_ex_model1 = baker.make(StageExecutionModel, state="test1")
#         stage_ex_model2 = baker.make(StageExecutionModel, state="test2")
#         ret = stage.StageExecution.filter(state='test1')
#
#         self.assertTrue(stage_ex_model1 in ret and stage_ex_model2 not in ret)
#
#     def test_filter_with_incorrect_param(self):
#         with self.assertRaises(exceptions.WrongParameterError):
#             stage.StageExecution.filter(incorrect='test1')
#
#     # def test__create_start_time(self):
#     #     stage_ex = stage.StageExecution(stage_execution_id=self.stage_ex_obj.model.id)
#     #     ret = stage_ex._StageExecution__create_start_time()
#     #
#     #     self.assertEqual(ret, stage_ex.model.plan_execution.start_time +
#     #                      datetime.timedelta(minutes=stage_ex.model.stage_model.trigger_args.get('minutes')))
#
#     # def test__create_start_time_with_pause_time(self):
#     #     stage_ex = stage.StageExecution(stage_execution_id=self.stage_ex_obj.model.id)
#     #     start_time = stage_ex.model.plan_execution.start_time
#     #
#     #     with patch.object(stage.StageExecution, 'start_time') as mock_start:
#     #         mock_start.__get__ = Mock(return_value=start_time + datetime.timedelta(minutes=-20))
#     #         with patch.object(stage.StageExecution, 'pause_time') as mock_pause:
#     #             mock_pause.__get__ = Mock(return_value=start_time + datetime.timedelta(minutes=-15))
#     #
#     #             ret = stage_ex._StageExecution__create_start_time()
#     #
#     #     self.assertEqual(ret, stage_ex.model.plan_execution.start_time + datetime.timedelta(minutes=5))
#     #
#     # def test__create_start_time_for_suspended_stage(self):
#     #     stage_ex = stage.StageExecution(stage_execution_id=self.stage_ex_obj.model.id)
#     #     stage_ex.state = 'PAUSED'
#     #     ret = stage_ex._StageExecution__create_start_time()
#     #
#     #     self.assertEqual(ret, stage_ex.model.plan_execution.start_time)
#
#     @patch('multiprocessing.Process', MagicMock)
#     @patch('threading.Thread', MagicMock)
#     @patch('cryton.hive.utility.util.split_into_lists', MagicMock(items=[]))
#     @patch('cryton.hive.etc.config.CPU_CORES', 0)
#     @patch('cryton.hive.utility.util.run_executions_in_threads', MagicMock)
#     @patch('django.db.connections.close_all', MagicMock)
#     def test_execute(self):
#         with patch.object(stage.StageExecution, 'state') as mock_state:
#             mock_state.__get__ = Mock(side_effect=['PENDING', 'RUNNING', 'FINISHED'])
#             with self.assertLogs('cryton-core-debug', level='INFO') as cm:
#                 self.stage_ex_obj.execute()
#
#         self.assertIn("Stage execution", cm.output[0])
#
#     @patch('multiprocessing.Process', MagicMock)
#     @patch('threading.Thread', MagicMock)
#     @patch('cryton.hive.utility.util.split_into_lists', MagicMock(items=[]))
#     @patch('cryton.hive.etc.config.CPU_CORES', 0)
#     @patch('cryton.hive.utility.util.run_executions_in_threads', MagicMock)
#     @patch('django.db.connections.close_all', MagicMock)
#     def test_execute_with_unfinished_dependency(self):
#
#         with patch.object(stage.StageExecution, 'state') as mock_state:
#             mock_state.__get__ = Mock(side_effect=['PENDING', 'RUNNING', 'FINISHED'])
#             with patch.object(stage.StageExecution, 'all_dependencies_finished') as mock_dependencies:
#                 mock_dependencies.__get__ = Mock(side_effect=[False])
#                 self.stage_ex_obj.execute()
#                 self.assertEqual('WAITING', self.stage_ex_obj.state)
#
#     @patch('multiprocessing.Process', MagicMock)
#     @patch('threading.Thread', MagicMock)
#     # @patch('cryton.hive.utility.split_into_lists', MagicMock(items=[]))
#     # @patch('cryton.hive.etc.config.CRYTON_CPU_CORES', 2)
#     @patch('cryton.hive.utility.util.run_executions_in_threads', MagicMock)
#     @patch('django.db.connections.close_all', MagicMock)
#     def test_execute_with_steps(self):
#         with open('{}/stage.yaml'.format(TESTS_DIR)) as fp:
#             stage_yaml = yaml.safe_load(fp)
#
#         stage_obj_id = creator.create_stage(stage_yaml, self.plan_model.id)
#
#         stage_exec = stage.StageExecution(stage_model_id=stage_obj_id,
#                                           plan_execution_id=self.plan_ex_model.id)
#         stage_exec.execute()
#
#     @patch('multiprocessing.Process', MagicMock)
#     @patch('threading.Thread', MagicMock)
#     @patch('cryton.hive.utility.util.split_into_lists', MagicMock(items=[]))
#     @patch('cryton.hive.etc.config.CPU_CORES', 0)
#     @patch('cryton.hive.utility.util.run_executions_in_threads', MagicMock)
#     @patch('django.db.connections.close_all', MagicMock)
#     def test_execute_pause(self):
#         PlanExecutionModel.objects.filter(id=self.stage_ex_obj.model.plan_execution_id).select_for_update() \
#             .update(state='PAUSING')
#
#         with self.assertLogs('cryton-core-debug', level='INFO') as cm:
#             self.assertEqual(self.stage_ex_obj.execute(), None)
#
#         for log in cm.output:
#             if 'Stage execution executed' in log:
#                 break
#         else:
#             raise AssertionError("'Stage execution executed' not found in log messages")
#
#     @patch('cryton.hive.triggers.trigger_delta.TriggerDelta._create_schedule_time')
#     @patch('cryton.hive.triggers.trigger_base.scheduler_client.schedule_function')
#     def test_schedule(self, schedule_function, schedule_time):
#         schedule_time.return_value = timezone.now()
#         schedule_function.return_value = '1'
#         with self.assertLogs('cryton-core-debug', level='INFO') as cm:
#             trigger_delta.TriggerDelta(self.stage_ex_obj).schedule()
#
#         self.assertIn("Stage execution scheduled", cm.output[0])
#         self.assertEqual(self.stage_ex_obj.aps_job_id, '1')
#
#     def test_schedule_not_delta(self):
#         stage_ex_model = baker.make(StageExecutionModel)
#         stage_ex = stage.StageExecution(stage_execution_id=stage_ex_model.id)
#
#         with self.assertRaises(exceptions.UnexpectedValue):
#             trigger_delta.TriggerDelta(stage_ex).schedule()
#
#     @patch('cryton.hive.triggers.trigger_base.scheduler_client.remove_job', MagicMock)
#     def test_unschedule(self):
#         self.stage_ex_obj.aps_job_id = '1'
#         with self.assertLogs('cryton-core-debug', level='INFO') as cm:
#             trigger_delta.TriggerDelta(self.stage_ex_obj).unschedule()
#
#         self.assertIn("Stage execution unscheduled", cm.output[0])
#         self.assertEqual(self.stage_ex_obj.aps_job_id, "")
#
#     @patch('cryton.hive.models.step.StepExecution.stop', Mock())
#     @patch('cryton.hive.models.stage.StageExecution.trigger', Mock())
#     def test_stop(self):
#         stage_ex_model = baker.make(StageExecutionModel, **{'state': 'RUNNING'})
#         baker.make(StepExecutionModel, **{'state': 'RUNNING', 'stage_execution': stage_ex_model})
#         stage_ex = stage.StageExecution(stage_execution_id=stage_ex_model.id)
#
#         with self.assertLogs('cryton-core-debug', level='INFO'):
#             stage_ex.stop()
#         self.assertEqual(stage_ex.state, 'STOPPED')
#
#     @patch('cryton.hive.triggers.trigger_delta.TriggerDelta.unschedule', Mock())
#     @patch('cryton.hive.models.stage.StageExecution.trigger', Mock())
#     def test_stop_scheduled(self):
#         stage_ex_model = baker.make(
#             StageExecutionModel, **{'state': 'PENDING', 'schedule_time': timezone.now(), 'stage_model':
#                 baker.make(StageModel, **{'trigger_type': 'delta', 'trigger_args': {}})})
#         stage_ex = stage.StageExecution(stage_execution_id=stage_ex_model.id)
#
#         with self.assertLogs('cryton-core-debug', level='INFO'):
#             stage_ex.stop()
#         self.assertEqual(stage_ex.state, 'STOPPED')
#
#     @patch('cryton.hive.models.stage.StageExecution.trigger', Mock())
#     def test_stop_waiting(self):
#         stage_ex_model = baker.make(StageExecutionModel, **{'state': 'WAITING'})
#         stage_ex = stage.StageExecution(stage_execution_id=stage_ex_model.id)
#
#         with self.assertLogs('cryton-core-debug', level='INFO'):
#             stage_ex.stop()
#         self.assertEqual(stage_ex.state, 'STOPPED')
#
#     # @patch('cryton.hive.models.step.StepExecution.validate_attack_module_args')
#     # def test_validate_modules(self, validate_args):
#     #     step_execution_model = baker.make(StepExecutionModel)
#     #     stage_execution = stage.StageExecution(stage_execution_id=step_execution_model.stage_execution.id)
#     #     validate_args.return_value = (True, 'ok')
#     #     ret = stage_execution.validate_modules()
#     #
#     #     self.assertEqual(ret, [(True, 'ok')])
#
#     def test_report(self):
#         plan_ex = baker.make(PlanExecutionModel, **{'state': 'RUNNING'})
#         stage_ex = baker.make(StageExecutionModel, **{'plan_execution': plan_ex, 'state': 'FINISHED',
#                                                       'aps_job_id': 'test_aps_id'})
#         step_ex = baker.make(StepExecutionModel, **{'stage_execution': stage_ex, 'state': 'FINISHED'})
#         stage_execution = stage.StageExecution(stage_execution_id=stage_ex.id)
#         report_dict = stage_execution.report()
#
#         self.assertIsInstance(report_dict, dict)
#         self.assertEqual(report_dict.get('state'), 'FINISHED')
#         self.assertIsNotNone(report_dict.get('step_executions'))
#         self.assertEqual(report_dict.get('step_executions')[0].get('state'), 'FINISHED')
#
#     @patch('cryton.hive.models.stage.StageExecution', MagicMock())
#     def test_execution(self):
#         self.assertIsNone(stage.execution(1))
#
#     @patch("cryton.hive.models.stage.StepExecutionWorkerExecute.validate", MagicMock())
#     def test_validate_modules(self):
#         stage_execution_model = baker.make(StageExecutionModel, **{'state': 'RUNNING'})
#         stage_execution = stage.StageExecution(stage_execution_id=stage_execution_model.id)
#         stage_execution.validate_modules()
#
#     @patch("cryton.hive.models.stage.StageExecution.reset_execution_data", Mock())
#     @patch("cryton.hive.models.stage.StageExecution.execute")
#     def test_re_execute_immediately(self, mock_execute):
#         self.stage_ex_obj.re_execute(True)
#         mock_execute.assert_called()
#
#     @patch("cryton.hive.models.stage.StageExecution.reset_execution_data", Mock())
#     def test_re_execute(self):
#         with patch("cryton.hive.models.stage.StageExecution.trigger") as mock_trigger:
#             self.stage_ex_obj.re_execute()
#             mock_trigger.start.assert_called()
#
#     @patch("cryton.hive.models.stage.StepExecution.reset_execution_data", Mock())
#     def test_reset_execution_data(self):
#         stage_ex_model = baker.make(StageExecutionModel, **{'state': 'STOPPED'})
#         stage_ex = stage.StageExecution(stage_execution_id=stage_ex_model.id)
#
#         stage_ex.reset_execution_data()
#         self.assertEqual(stage_ex.state, "PENDING")
#
#     def test_finish(self):
#         mock_execute_subjects_to_dependency = Mock()
#         self.stage_ex_obj.execute_subjects_to_dependency = mock_execute_subjects_to_dependency
#
#         self.stage_ex_obj.finish()
#
#         assert self.stage_ex_obj.state == "FINISHED"
#         assert self.stage_ex_obj.finish_time is not None
#         mock_execute_subjects_to_dependency.assert_called_once()

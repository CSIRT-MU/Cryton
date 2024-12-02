# from datetime import datetime, timezone
#
# from django.test import TestCase
# from unittest.mock import patch, Mock, MagicMock, call
# from model_bakery import baker
#
# from cryton.hive.utility import exceptions, logger
# from cryton.hive.models import plan
#
# from cryton.hive.cryton_app.models import PlanModel, StageModel, StepExecutionModel, StageExecutionModel, \
#     PlanExecutionModel, WorkerModel, RunModel
#
# from cryton.hive.triggers import trigger_http
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger('cryton-core-debug'))
# class PlanTest(TestCase):
#     def setUp(self):
#         self.plan_obj = plan.Plan(plan_model_id=baker.make(PlanModel).id)
#
#     def test_constructor_existing(self):
#         plan_model = baker.make(PlanModel)
#
#         plan_obj = plan.Plan(plan_model_id=plan_model.id)
#
#         self.assertEqual(plan_obj.model, plan_model)
#
#     def test_constructor_existing_invalid(self):
#         with self.assertRaises(exceptions.PlanObjectDoesNotExist):
#             plan.Plan(plan_model_id=42)
#
#     def test_constructor_create(self):
#         plan_obj = plan.Plan(owner="tester", name="test name")
#
#         self.assertEqual(plan_obj.owner, "tester")
#         self.assertEqual(plan_obj.dynamic, False)
#
#     def test_filter_all(self):
#         plan_model1 = baker.make(PlanModel)
#         plan_model2 = baker.make(PlanModel)
#
#         ret = plan.Plan.filter()
#
#         self.assertTrue(plan_model1 in ret)
#         self.assertTrue(plan_model2 in ret)
#
#     def test_filter_field(self):
#         plan_model1 = baker.make(PlanModel, name="name 1")
#         plan_model2 = baker.make(PlanModel, name="name 2")
#
#         ret = plan.Plan.filter(name="name 1")
#
#         self.assertTrue(plan_model1 in ret)
#         self.assertTrue(plan_model2 not in ret)
#
#     def test_filter_invalid_field(self):
#         with self.assertRaises(exceptions.WrongParameterError):
#             plan.Plan.filter(invalid="test")
#
#     def test_name_property(self):
#         self.plan_obj.name = "testname"
#         self.assertEqual(self.plan_obj.name, "testname")
#
#     def test_owner_property(self):
#         self.plan_obj.owner = "testowner"
#         self.assertEqual(self.plan_obj.owner, "testowner")
#
#     def test_evidence_dir_property(self):
#         self.plan_obj.evidence_dir = "testdir"
#         self.assertEqual(self.plan_obj.evidence_dir, "testdir")
#
#     def test_dynamic_property(self):
#         self.plan_obj.dynamic = True
#         self.assertEqual(self.plan_obj.dynamic, True)
#
#     def test_delete(self):
#         plan_model_id = self.plan_obj.model.id
#
#         self.assertIsInstance(plan_model_id, int)
#
#         self.plan_obj.delete()
#
#         with self.assertRaises(exceptions.PlanObjectDoesNotExist):
#             plan.Plan(plan_model_id=plan_model_id)
#
#     @patch("cryton.hive.models.plan.Plan.validate_unique_values", Mock)
#     @patch("cryton.hive.models.stage.Stage.validate")
#     def test_validate_all_valid(self, mock_stage_validate):
#         stage1 = {
#             "name": "stage1", "steps": [
#                 {"name": "step1"}, {"name": "step2"}
#             ]
#         }
#         stage2 = {
#             "name": "stage2", "steps": [
#                 {"name": "step3"}, {"name": "step4"}
#             ]
#         }
#
#         args = {
#             "name": "test",
#             "owner": "tester",
#             "stages": [stage1, stage2]
#         }
#
#         plan.Plan.validate(args)
#
#         mock_stage_validate.assert_has_calls([call(stage1, False), call(stage2, False)])
#
#     @patch("cryton.hive.models.stage.Stage.validate", Mock)
#     def test_validate_stage_dependency(self):
#         test_plan_dict = {
#             "name": "Test plan",
#             "owner": "tester",
#             "stages": [
#                 {
#                     "name": "stage2",
#                     "depends_on": ["stage1"],
#                     "steps": []
#                 }
#             ]
#         }
#
#         with self.assertRaises(exceptions.PlanValidationError) as err:
#             plan.Plan.validate(test_plan_dict)
#
#         self.assertEqual(err.exception.message, {'message': "Stage dependency 'stage1' does not exist in the plan",
#                                'plan_name': 'Test plan'})
#
#     def test_validate_unique_stage_names(self):
#         test_plan_dict = {
#             "name": "Test plan",
#             "owner": "test name",
#             "stages": [
#                 {
#                     "name": "stage-one",
#                     "trigger_type": "delta",
#                     "trigger_args": {
#                         "seconds": 5
#                     },
#                     "steps": []
#                 },
#                 {
#                     "name": "stage-one",
#                     "trigger_type": "delta",
#                     "trigger_args": {
#                         "seconds": 5
#                     },
#                     "steps": []
#                 }
#             ]
#         }
#         with self.assertRaises(exceptions.DuplicateNameInPlan) as err:
#             plan.Plan.validate_unique_values(test_plan_dict)
#
#         self.assertEqual(err.exception.message, {'message': "Stage name 'stage-one' is not unique in the plan",
#                                                  'plan_name': 'Test plan'})
#
#     def test_validate_unique_step_names(self):
#         test_plan_dict = {
#             "name": "Test plan",
#             "owner": "test name",
#             "stages": [
#                 {
#                     "name": "stage-one",
#                     "trigger_type": "delta",
#                     "trigger_args": {
#                         "seconds": 5
#                     },
#                     "steps": [
#                         {
#                             "name": "scan-localhost",
#                             "is_init": True,
#                             "step_type": "worker/execute",
#                             "arguments": {},
#                         },
#                         {
#                             "name": "scan-localhost",
#                             "is_init": True,
#                             "step_type": "worker/execute",
#                             "arguments": {}
#                         }
#                     ]
#                 }
#             ]
#         }
#         with self.assertRaises(exceptions.DuplicateNameInPlan) as err:
#             plan.Plan.validate_unique_values(test_plan_dict)
#
#         self.assertEqual(err.exception.message, {'message': "Step name 'scan-localhost' is not unique in the plan",
#                                                  'plan_name': 'Test plan'})
#
#     def test_validate_unique_session_names(self):
#         test_plan_dict = {
#             "name": "Test plan",
#             "owner": "test name",
#             "stages": [
#                 {
#                     "name": "stage-one",
#                     "trigger_type": "delta",
#                     "trigger_args": {
#                         "seconds": 5
#                     },
#                     "steps": [
#                         {
#                             "name": "create_session1",
#                             "is_init": True,
#                             "step_type": "worker/execute",
#                             "arguments": {
#                                 "create_named_session": "test_session"
#                             },
#                         },
#                         {
#                             "name": "create_session2",
#                             "is_init": True,
#                             "step_type": "worker/execute",
#                             "arguments": {
#                                 "create_named_session": "test_session"
#                             }
#                         }
#                     ]
#                 }
#             ]
#         }
#
#         with self.assertRaises(exceptions.DuplicateNameInPlan) as err:
#             plan.Plan.validate_unique_values(test_plan_dict)
#
#         self.assertEqual(err.exception.message, {'message': "Session name 'test_session' is not unique in the plan",
#                                                  'plan_name': 'Test plan'})
#
#     def test_validate_unique_empire_agent_names(self):
#         test_plan_dict = {
#             "name": "Test plan",
#             "owner": "test name",
#             "stages": [
#                 {
#                     "name": "stage-one",
#                     "trigger_type": "delta",
#                     "trigger_args": {
#                         "seconds": 5
#                     },
#                     "steps": [
#                         {
#                             "name": "deploy_agent1",
#                             "is_init": True,
#                             "step_type": "empire/agent-deploy",
#                             "arguments": {
#                                 "agent_name": "test_agent"
#                             },
#                         },
#                         {
#                             "name": "deploy_agent2",
#                             "is_init": True,
#                             "step_type": "empire/agent-deploy",
#                             "arguments": {
#                                 "agent_name": "test_agent"
#                             }
#                         }
#                     ]
#                 }
#             ]
#         }
#
#         with self.assertRaises(exceptions.DuplicateNameInPlan) as err:
#             plan.Plan.validate_unique_values(test_plan_dict)
#
#         self.assertEqual(err.exception.message, {'message': "Empire Agent name 'test_agent' is not unique in the plan",
#                                                  'plan_name': 'Test plan'})
#
#     def test_validate_missing(self):
#         args = {"owner": "tester", "stages": [{"stage1": "..."}]}
#
#         with self.assertRaises(exceptions.PlanValidationError):
#             plan.Plan.validate(args)
#
#         args = {"name": "test", "owner": "tester"}
#
#         with self.assertRaises(exceptions.PlanValidationError):
#             plan.Plan.validate(args)
#
#     def test_validate_invalid_type(self):
#         args = {"name": "test", "owner": "tester", "stages": {}}
#
#         with self.assertRaises(exceptions.PlanValidationError):
#             plan.Plan.validate(args)
#
#         args = {"name": "test", "owner": 42, "stages": [{"stage1": "..."}]}
#
#         with self.assertRaises(exceptions.PlanValidationError):
#             plan.Plan.validate(args)
#
#     def test_validate_empty_stages(self):
#         args = {"name": "test", "owner": "tester", "stages": []}
#
#         with self.assertRaises(exceptions.PlanValidationError):
#             plan.Plan.validate(args)
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger('cryton-core-debug'))
# @patch('cryton.hive.utility.states.PlanStateMachine.validate_transition', MagicMock())
# class PlanExecutionTest(TestCase):
#     def setUp(self):
#         self.pex_obj = plan.PlanExecution(plan_execution_id=baker.make(PlanExecutionModel).id)
#
#     def test_constructor_existing(self):
#         plan_execution_model = baker.make(PlanExecutionModel)
#
#         plan_execution = plan.PlanExecution(plan_execution_id=plan_execution_model.id)
#
#         self.assertEqual(plan_execution.model, plan_execution_model)
#
#     def test_constructor_existing_invalid(self):
#         with self.assertRaises(exceptions.PlanExecutionDoesNotExist):
#             plan.PlanExecution(plan_execution_id=42)
#
#     @patch("cryton.hive.models.plan.PlanExecution._create_evidence_directory")
#     def test_constructor_create(self, mock_evidence_directory):
#         run_model = baker.make(RunModel)
#         worker_model = baker.make(WorkerModel)
#         plan_instance_model = baker.make(PlanModel)
#
#         plan_execution = plan.PlanExecution(run=run_model, worker=worker_model, plan_model_id=plan_instance_model.id)
#
#         self.assertEqual(plan_execution.model.run, run_model)
#         self.assertEqual(plan_execution.model.worker, worker_model)
#         mock_evidence_directory.assert_called_once()
#
#     def test_state_property(self):
#         self.pex_obj.state = "RUNNING"
#         self.assertEqual(self.pex_obj.state, "RUNNING")
#
#     def test_start_time_property(self):
#         time = datetime(3000, 12, 12, 10, 10, 10, tzinfo=timezone.utc)
#
#         self.pex_obj.start_time = time
#         self.assertEqual(self.pex_obj.start_time, time)
#
#     def test_pause_time_property(self):
#         time = datetime(3000, 12, 12, 10, 10, 10, tzinfo=timezone.utc)
#
#         self.pex_obj.pause_time = time
#         self.assertEqual(self.pex_obj.pause_time, time)
#
#     def test_finish_time_property(self):
#         time = datetime(3000, 12, 12, 10, 10, 10, tzinfo=timezone.utc)
#
#         self.pex_obj.finish_time = time
#         self.assertEqual(self.pex_obj.finish_time, time)
#
#     def test_aps_job_id_property(self):
#         self.pex_obj.aps_job_id = "42"
#         self.assertEqual(self.pex_obj.aps_job_id, "42")
#
#     def test_evidence_directory_property(self):
#         self.pex_obj.evidence_directory = "testdir"
#         self.assertEqual(self.pex_obj.evidence_directory, "testdir")
#
#     def test_delete(self):
#         pex_model_id = self.pex_obj.model.id
#
#         self.assertIsInstance(pex_model_id, int)
#
#         self.pex_obj.delete()
#
#         with self.assertRaises(exceptions.PlanExecutionDoesNotExist):
#             plan.PlanExecution(plan_execution_id=pex_model_id)
#
#     @patch("cryton.hive.utility.scheduler_client.schedule_function", Mock(return_value=1))
#     def test_schedule(self):
#         stage_execution_model = baker.make(StageExecutionModel,
#                                            stage_model=baker.make(StageModel, trigger_type="delta"),
#                                            state="PENDING")
#         plan_execution = plan.PlanExecution(plan_execution_id=stage_execution_model.plan_execution.id)
#
#         with self.assertLogs('cryton-core-debug', level='INFO') as cm:
#             plan_execution.schedule(datetime(3000, 12, 12, 10, 0, 0, tzinfo=timezone.utc))
#
#         self.assertEqual(plan_execution.state, "SCHEDULED")
#         self.assertEqual(plan_execution.schedule_time, datetime(3000, 12, 12, 10, 0, 0, tzinfo=timezone.utc))
#         self.assertIn("Plan execution scheduled", cm.output[0])
#
#     @patch("cryton.hive.models.plan.PlanExecution.start_triggers")
#     @patch('cryton.hive.models.plan.worker.Worker', Mock())
#     def test_execute_delta_stage_pending(self, mock_start_triggers):
#         stage_execution_model = baker.make(StageExecutionModel,
#                                            stage_model=baker.make(StageModel, trigger_type="delta"),
#                                            state="PENDING")
#         plan_execution = plan.PlanExecution(plan_execution_id=stage_execution_model.plan_execution.id)
#         with self.assertLogs('cryton-core-debug', level='INFO') as cm:
#             plan_execution.execute()
#
#         mock_start_triggers.assert_called_once()
#         self.assertEqual(plan_execution.state, "RUNNING")
#         self.assertIn("Plan execution executed", cm.output[0])
#
#     @patch("cryton.hive.models.plan.PlanExecution.start_triggers")
#     @patch('cryton.hive.models.plan.worker.Worker', Mock())
#     def test_execute_delta_stage_suspended(self, mock_start_triggers):
#         stage_execution_model = baker.make(StageExecutionModel,
#                                            stage_model=baker.make(StageModel, trigger_type="delta"),
#                                            state="PAUSED")
#         plan_execution = plan.PlanExecution(plan_execution_id=stage_execution_model.plan_execution.id)
#
#         with self.assertLogs('cryton-core-debug', level='INFO') as cm:
#             plan_execution.execute()
#
#         mock_start_triggers.assert_called_once()
#         self.assertEqual(plan_execution.state, "RUNNING")
#         self.assertIn("Plan execution executed", cm.output[0])
#
#     @patch("cryton.hive.models.plan.PlanExecution.start_triggers")
#     @patch('cryton.hive.models.plan.worker.Worker', Mock())
#     def test_execute_delta_stage_running(self, mock_start_triggers):
#         stage_execution_model = baker.make(StageExecutionModel,
#                                            stage_model=baker.make(StageModel, trigger_type="delta"),
#                                            state="RUNNING")
#         plan_execution = plan.PlanExecution(plan_execution_id=stage_execution_model.plan_execution.id)
#
#         with self.assertLogs('cryton-core-debug', level='INFO') as cm:
#             plan_execution.execute()
#
#         mock_start_triggers.assert_called_once()
#         self.assertEqual(plan_execution.state, "RUNNING")
#         self.assertIn("Plan execution executed", cm.output[0])
#
#     @patch("cryton.hive.triggers.trigger_delta.TriggerDelta.schedule")
#     @patch("cryton.hive.models.plan.PlanExecution.start_triggers")
#     @patch('cryton.hive.models.plan.worker.Worker', Mock())
#     def test_execute_trigger_stage(self, mock_start_triggers, mock_schedule_stage):
#         stage_execution_model = baker.make(StageExecutionModel,
#                                            stage_model=baker.make(StageModel, trigger_type="HTTPListener"))
#         plan_execution = plan.PlanExecution(plan_execution_id=stage_execution_model.plan_execution.id)
#
#         with self.assertLogs('cryton-core-debug', level='INFO') as cm:
#             plan_execution.execute()
#
#         mock_start_triggers.assert_called_once()
#         mock_schedule_stage.assert_not_called()
#         self.assertEqual(plan_execution.state, "RUNNING")
#         self.assertIn("Plan execution executed", cm.output[0])
#
#     @patch("cryton.hive.models.plan.PlanExecution.start_triggers", Mock())
#     def test_execute_not_pending(self):
#         stage_execution_model = baker.make(StageExecutionModel,
#                                            stage_model=baker.make(StageModel, trigger_type="HTTPListener"))
#         plan_execution = plan.PlanExecution(plan_execution_id=stage_execution_model.plan_execution.id)
#         plan_execution.state = "RUNNING"
#
#         with self.assertRaises(exceptions.PlanInvalidStateError), self.assertLogs('cryton-core-debug', level='WARNING')\
#                 as cm:
#             plan_execution.execute()
#             self.assertIn("invalid state detected", cm.output[0])
#
#     @patch("cryton.hive.models.plan.scheduler_client.remove_job")
#     def test_unschedule(self, mock_schedule):
#         plan_execution_model = baker.make(PlanExecutionModel, state="SCHEDULED",
#                                           stage_executions=[baker.make(StageExecutionModel,
#                                                                        stage_model=baker.make(StageModel,
#                                                                                               trigger_type="delta"))])
#         plan_execution = plan.PlanExecution(plan_execution_id=plan_execution_model.id)
#
#         with self.assertLogs('cryton-core-debug', level='INFO') as cm:
#             plan_execution.unschedule()
#
#         self.assertEqual(plan_execution.state, "PENDING")
#         mock_schedule.assert_called_once()
#         self.assertIn("Plan execution unscheduled", cm.output[0])
#
#     def test_unschedule_invalid_state(self):
#         plan_execution_model = baker.make(PlanExecutionModel, state="RUNNING")
#         plan_execution = plan.PlanExecution(plan_execution_id=plan_execution_model.id)
#
#         with self.assertRaises(exceptions.PlanInvalidStateError), self.assertLogs('cryton-core-debug', level='WARNING')\
#                 as cm:
#             plan_execution.unschedule()
#             self.assertIn("invalid state detected", cm.output[0])
#
#     @patch("cryton.hive.models.plan.PlanExecution.schedule")
#     @patch("cryton.hive.models.plan.PlanExecution.unschedule")
#     def test_reschedule_valid(self, mock_unschedule_plan, mock_schedule_plan):
#         plan_execution_model = baker.make(PlanExecutionModel, start_time="3000-12-12 10:00:00Z", state="SCHEDULED")
#         plan_execution = plan.PlanExecution(plan_execution_id=plan_execution_model.id)
#
#         with self.assertLogs('cryton-core-debug', level='INFO') as cm:
#             plan_execution.reschedule(datetime(3000, 12, 12, 11, 1, 1, tzinfo=timezone.utc))
#
#         mock_schedule_plan.assert_called_with(datetime(3000, 12, 12, 11, 1, 1, tzinfo=timezone.utc))
#         mock_unschedule_plan.assert_called_once()
#         self.assertIn("Plan execution rescheduled", cm.output[0])
#
#     def test_reschedule_datetime_invalid(self):
#         plan_execution_model = baker.make(PlanExecutionModel, start_time="3000-12-12 10:00:00Z", state="SCHEDULED")
#         plan_execution = plan.PlanExecution(plan_execution_id=plan_execution_model.id)
#
#         with self.assertRaises(exceptions.UserInputError), self.assertLogs('cryton-core-debug', level='ERROR'):
#             plan_execution.reschedule(datetime(1990, 12, 12, 11, 1, 1, tzinfo=timezone.utc))
#
#     @patch("cryton.hive.models.plan.PlanExecution.schedule", Mock())
#     @patch("cryton.hive.models.plan.PlanExecution.unschedule", Mock())
#     def test_reschedule_notscheduled(self):
#         plan_execution_model = baker.make(PlanExecutionModel, start_time="3000-12-12 10:00:00Z", state="PENDING")
#         plan_execution = plan.PlanExecution(plan_execution_id=plan_execution_model.id)
#
#         with self.assertRaises(exceptions.PlanInvalidStateError), self.assertLogs('cryton-core-debug', level='ERROR'):
#             plan_execution.reschedule(datetime(3000, 12, 12, 11, 1, 1))
#
#     @patch("cryton.hive.triggers.trigger_delta.TriggerDelta.pause")
#     def test_pause_pending_stage(self, mock_stage_pause):
#         stage_execution_model = baker.make(StageExecutionModel, state="PENDING",
#                                            stage_model=baker.make(StageModel, trigger_type="delta",
#                                                                   trigger_args={}))
#         plan_execution = plan.PlanExecution(plan_execution_id=stage_execution_model.plan_execution.id)
#         plan_execution.state = "RUNNING"
#
#         with self.assertLogs('cryton-core-debug', level='INFO') as cm:
#             plan_execution.pause()
#
#         self.assertEqual(plan_execution.state, "PAUSED")
#         mock_stage_pause.assert_called_once()
#         self.assertIn("Plan execution pausing", cm.output[0])
#
#     @patch("cryton.hive.triggers.trigger_delta.TriggerDelta.pause")
#     def test_pause_suspended_stage(self, mock_stage_pause):
#         stage_execution_model = baker.make(StageExecutionModel, state="PAUSED",
#                                            stage_model=baker.make(StageModel, trigger_type="delta",
#                                                                   trigger_args={})
#                                            )
#         plan_execution = plan.PlanExecution(plan_execution_id=stage_execution_model.plan_execution.id)
#         plan_execution.state = "RUNNING"
#
#         with self.assertLogs('cryton-core-debug', level='INFO') as cm:
#             plan_execution.pause()
#
#         self.assertEqual(plan_execution.state, "PAUSED")
#         mock_stage_pause.assert_called_once()
#         self.assertIn("Plan execution pausing", cm.output[0])
#
#     @patch("cryton.hive.triggers.trigger_delta.TriggerDelta.unschedule")
#     def test_pause_running_stage(self, mock_stage_pause):
#         stage_execution_model = baker.make(StageExecutionModel, state="RUNNING",
#                                            stage_model=baker.make(StageModel, trigger_type="delta",
#                                                                   trigger_args={})
#                                            )
#         plan_execution = plan.PlanExecution(plan_execution_id=stage_execution_model.plan_execution.id)
#         plan_execution.state = "RUNNING"
#
#         with self.assertLogs('cryton-core-debug', level='INFO'):
#             plan_execution.pause()
#
#         self.assertEqual(plan_execution.state, "PAUSING")
#         mock_stage_pause.assert_not_called()
#
#     @patch('cryton.hive.models.plan.datetime')
#     @patch("cryton.hive.triggers.trigger_delta.TriggerDelta.resume")
#     def test_resume_stage(self, mock_stage_resume, mock_utcnow):
#         mock_utcnow.now.return_value = datetime(3000, 12, 12, 10, 0, 0, tzinfo=timezone.utc)
#         stage_execution_model = baker.make(StageExecutionModel, state="PAUSED",
#                                            stage_model=baker.make(StageModel, trigger_type="delta",
#                                                                   trigger_args={})
#                                            )
#         plan_execution = plan.PlanExecution(plan_execution_id=stage_execution_model.plan_execution.id)
#         plan_execution.state = "PAUSED"
#
#         plan_execution.resume()
#
#         self.assertEqual(plan_execution.state, "RUNNING")
#         mock_stage_resume.assert_called()
#
#     @patch("cryton.hive.triggers.trigger_delta.TriggerDelta.unschedule")
#     def test_pause_suspending_stage(self, mock_stage_unschedule):
#         stage_execution_model = baker.make(StageExecutionModel, state="PAUSING",
#                                            stage_model=baker.make(StageModel, trigger_type="delta",
#                                                                   trigger_args={})
#                                            )
#         plan_execution = plan.PlanExecution(plan_execution_id=stage_execution_model.plan_execution.id)
#         plan_execution.state = "RUNNING"
#
#         with self.assertLogs('cryton-core-debug', level='INFO'):
#             plan_execution.pause()
#
#         self.assertEqual(plan_execution.state, "PAUSING")
#         mock_stage_unschedule.assert_not_called()
#
#     # @patch("cryton.hive.stage.StageExecution.validate_modules")
#     # def test_validate_modules(self, mock_stage_validate_modules):
#     #     mock_stage_validate_modules.return_value = [(True, None), (False, "error 1")]
#     #     stage_execution_model = baker.make(StageExecutionModel)
#     #     plan_execution = plan.PlanExecution(plan_execution_id=stage_execution_model.plan_execution.id)
#     #
#     #     ret = plan_execution.validate_modules()
#     #
#     #     self.assertEqual(ret, [(True, None), (False, "error 1")])
#     #
#     # @patch("cryton.hive.stage.StageExecution.validate_modules")
#     # def test_validate_modules_more_stages(self, mock_stage_validate_modules):
#     #     mock_stage_validate_modules.side_effect = [[(True, None), (False, "error 1")],
#     #                                                [(True, None), (False, "error 2")]]
#     #     stage_execution_model_1 = baker.make(StageExecutionModel)
#     #     stage_execution_model_2 = baker.make(StageExecutionModel)
#     #     plan_execution = plan.PlanExecution(plan_execution_id=baker.make(PlanExecutionModel,
#     #                                                                      stage_executions=[stage_execution_model_1,
#     #                                                                                        stage_execution_model_2]).id)
#     #
#     #     ret = plan_execution.validate_modules()
#     #
#     #     self.assertEqual(ret, [(True, None), (False, "error 1"), (True, None), (False, "error 2")])
#
#     @patch("cryton.hive.models.plan.os.makedirs")
#     @patch("cryton.hive.models.plan.config.EVIDENCE_DIRECTORY", "/path")
#     def test_create_evidence_directory(self, mock_makedirs):
#         plan_execution_model = baker.make(PlanExecutionModel,
#                                           run=baker.make(RunModel,
#                                                          plan_model=baker.make(PlanModel)),
#                                           worker=baker.make(WorkerModel, name='test_worker')
#                                           )
#         plan_execution = plan.PlanExecution(plan_execution_id=plan_execution_model.id)
#         expected_path = f"/path/run_{plan_execution_model.run.id}/worker_{plan_execution_model.worker.name}"
#
#         plan_execution._create_evidence_directory()
#
#         self.assertEqual(plan_execution.evidence_directory, expected_path)
#         mock_makedirs.assert_called_with(expected_path, exist_ok=True)
#
#     def test_start_triggers(self):
#         mock_start_http_listener = Mock()
#         stage_execution_model = baker.make(StageExecutionModel,
#                                            stage_model=baker.make(StageModel, trigger_type="HTTPListener",
#                                                                   trigger_args={}))
#         plan_execution_model = baker.make(PlanExecutionModel, stage_executions=[stage_execution_model])
#         plan_execution = plan.PlanExecution(plan_execution_id=plan_execution_model.id)
#         # ._PlanExecution__start_http_listener = mock_start_http_listener
#         trigger_http.TriggerHTTP.start = mock_start_http_listener
#         # expected_args = {"plan_execution_id": plan_execution_model.id, "stage_id": stage_execution_model.stage_model.id}
#
#         plan_execution.start_triggers()
#
#         # mock_start_http_listener.assert_called_once_with(expected_args)
#         mock_start_http_listener.assert_called_once()
#
#     def test_filter_all(self):
#         plan_execution_model1 = baker.make(PlanExecutionModel)
#         plan_execution_model2 = baker.make(PlanExecutionModel)
#
#         ret = plan.PlanExecution.filter()
#
#         self.assertTrue(plan_execution_model1 in ret)
#         self.assertTrue(plan_execution_model2 in ret)
#
#     def test_filter_field(self):
#         plan_execution_model1 = baker.make(PlanExecutionModel, state="PENDING")
#         plan_execution_model2 = baker.make(PlanExecutionModel, state="RUNNING")
#
#         ret = plan.PlanExecution.filter(state="PENDING")
#
#         self.assertTrue(plan_execution_model1 in ret)
#         self.assertTrue(plan_execution_model2 not in ret)
#
#     def test_filter_invalid_field(self):
#         with self.assertRaises(exceptions.WrongParameterError):
#             plan.PlanExecution.filter(invalid="test")
#
#     def test_report(self):
#         plan_execution_model = baker.make(PlanExecutionModel, **{'state': 'RUNNING'})
#         stage_ex = baker.make(StageExecutionModel, **{'plan_execution': plan_execution_model, 'state': 'FINISHED',
#                                                       'aps_job_id': 'test_aps_id'})
#         step_ex = baker.make(StepExecutionModel, **{'stage_execution': stage_ex, 'state': 'FINISHED'})
#         plan_execution = plan.PlanExecution(plan_execution_id=plan_execution_model.id)
#         report_dict = plan_execution.report()
#
#         self.assertIsInstance(report_dict, dict)
#         self.assertEqual(report_dict.get('stage_executions')[0].get('state'), 'FINISHED')
#         self.assertIsNotNone(report_dict.get('stage_executions')[0].get('step_executions'))
#         self.assertEqual(report_dict.get('stage_executions')[0].get('step_executions')[0]
#                          .get('state'), 'FINISHED')
#
#     @patch("cryton.hive.models.plan.PlanExecution.execute", MagicMock())
#     def test_execution(self):
#         plan.execution(self.pex_obj.model.id)
#         self.pex_obj.execute.assert_called()
#
#     @patch("cryton.hive.models.stage.StageExecution.validate_modules", MagicMock())
#     def test_validate_modules(self):
#         plan_execution_model = baker.make(PlanExecutionModel, **{'state': 'RUNNING'})
#         plan_execution = plan.PlanExecution(plan_execution_id=plan_execution_model.id)
#         plan_execution.validate_modules()
#
#     @patch('cryton.hive.models.plan.connections.close_all', Mock())
#     @patch('cryton.hive.models.stage.StageExecution.stop', Mock())
#     def test_stop(self):
#         plan_execution_model = baker.make(PlanExecutionModel, **{'state': 'RUNNING'})
#         baker.make(StageExecutionModel, **{'state': 'RUNNING', 'plan_execution': plan_execution_model})
#         plan_execution = plan.PlanExecution(plan_execution_id=plan_execution_model.id)
#
#         with self.assertLogs('cryton-core-debug', level='INFO'):
#             plan_execution.stop()
#         self.assertEqual(plan_execution.state, 'STOPPED')

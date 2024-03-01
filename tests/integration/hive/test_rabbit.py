# from django.test import TestCase
# import yaml
# import os
#
# from unittest.mock import patch, Mock, MagicMock
#
# from cryton.hive.utility import creator, logger, states
# from cryton.hive.models import stage, plan, run, worker
#
# import threading
#
# TESTS_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger('cryton-core-test'))
# @patch("amqpstorm.Connection", MagicMock())
# class TestRabbit(TestCase):
#
#     def setUp(self):
#         worker_id = creator.create_worker('tt', '192.168.56.130')
#         self.worker = worker.Worker(worker_model_id=worker_id)
#         self.workers = [self.worker.model]
#
#     @patch("cryton.hive.triggers.trigger_delta.TriggerDelta.schedule")
#     @patch('django.db.connections.close_all', Mock)
#     def test_whole_plan_execution(self, mock_stage_schedule):
#         with open(TESTS_DIR + '/plan.yaml') as plan_yaml:
#             plan_dict = yaml.safe_load(plan_yaml)
#
#         plan_obj_id = creator.create_plan(plan_dict)
#         run_obj = run.Run(plan_model_id=plan_obj_id, workers=self.workers)
#         plan_ex_obj = plan.PlanExecution(plan_execution_id=plan.PlanExecutionModel.objects.get(
#             run_id=run_obj.model.id).id)
#         stage_ex_obj = stage.StageExecution(stage_execution_id=stage.StageExecutionModel.objects.get(
#             plan_execution_id=plan_ex_obj.model.id).id)
#
#         def se():
#             stage_ex_obj.state = states.SCHEDULED
#             t = threading.Thread(stage.execution(stage_ex_obj.model.id))
#             t.run()
#
#         mock_stage_schedule.side_effect = se
#
#         run_obj.execute()
#
#         self.assertEqual(run_obj.state, states.RUNNING)
#         self.assertEqual(plan_ex_obj.state, states.RUNNING)
#         self.assertEqual(stage_ex_obj.state, states.RUNNING)

# from pytest_mock import MockerFixture
# from unittest import TestCase
# from unittest.mock import patch, Mock
# from schema import SchemaError
#
# import amqpstorm
#
# from cryton.worker import task
# from cryton.worker.util import constants as co, logger
#
#
# @patch('cryton.worker.util.logger.logger', logger.structlog.getLogger("cryton-worker-test"))
# class TestTask(TestCase):
#     @patch("multiprocessing.Process", Mock())
#     # @patch("cryton.worker.task.get_context.Process", Mock())
#     def setUp(self):
#         self.mock_main_queue = Mock()
#         self.message = Mock()
#         self.connection = Mock()
#         self.task_obj = task.Task(self.message, self.mock_main_queue, self.connection)
#
#     @patch("json.dumps", Mock())
#     @patch("json.loads", Mock())
#     @patch("cryton.worker.task.Task._execute", Mock())
#     @patch("cryton.worker.task.Task._validate", Mock())
#     @patch("cryton.worker.task.Task.reply", Mock())
#     @patch("cryton.worker.task.Task.send_ack", Mock())
#     def test___call__(self):
#         self.task_obj()
#         self.mock_main_queue.put.assert_called_once()
#
#     @patch("json.dumps")
#     @patch("json.loads", Mock())
#     @patch("cryton.worker.task.Task._execute", Mock())
#     @patch("cryton.worker.task.Task._validate")
#     @patch("cryton.worker.task.Task.reply", Mock())
#     @patch("cryton.worker.task.Task.send_ack", Mock())
#     def test___call___err(self, mock_validate, mock_dumps):
#         mock_validate.side_effect = SchemaError("")
#         self.task_obj()
#         mock_dumps.assert_called_once_with({"return_code": -2, "output": ""})
#         self.mock_main_queue.put.assert_called_once()
#
#     def test__validate(self):
#         self.task_obj._validate({})
#
#     def test__execute(self):
#         self.task_obj._execute({})
#
#     def test_stop(self):
#         mock_process = Mock()
#         mock_process.pid = "pid"
#         mock_process.exitcode = None
#         self.task_obj._process = mock_process
#         result = self.task_obj.stop()
#
#         assert result
#
#     def test_stop_not_started(self):
#         result = self.task_obj.stop()
#
#         assert not result
#
#     def test_stop_finished(self):
#         mock_process = Mock()
#         mock_process.pid = "pid"
#         mock_process.exitcode = 0
#         self.task_obj._process = mock_process
#         result = self.task_obj.stop()
#
#         assert not result
#
#     @patch("cryton.worker.task.Task.__call__", Mock())
#     def test_start(self):
#         self.assertIsNone(self.task_obj.start())
#
#     @patch("amqpstorm.Message.create")
#     def test_reply(self, mock_create):
#         result = self.task_obj.reply("")
#
#         assert result is True
#         mock_create.assert_called_once()
#
#     def test_reply_fail(self):
#         self.task_obj._connection.channel.side_effect = amqpstorm.AMQPError
#
#         result = self.task_obj.reply("")
#
#         assert result is False
#
#     def test_send_ack(self):
#         mock_main_queue = Mock()
#         task_obj = task.Task(Mock(), mock_main_queue, self.connection)
#         task_obj.correlation_id = "id"
#
#         mock_reply = Mock()
#         task_obj.reply = mock_reply
#
#         task_obj.send_ack("ack_queue")
#
#         mock_reply.assert_called_once_with('{"return_code": 0}', 'ack_queue')
#
#
# @patch('cryton.worker.util.logger.logger', logger.structlog.getLogger("cryton-worker-test"))
# class TestAttackTask(TestCase):
#     @patch("cryton.worker.task.Process", Mock())
#     def setUp(self):
#         self.mock_main_queue = Mock()
#         self.message = Mock()
#         self.connection = Mock()
#         self.task_obj = task.AttackTask(self.message, self.mock_main_queue, self.connection)
#
#     def test__validate(self):
#         self.task_obj._validate({co.ARGUMENTS: {co.MODULE: "", co.MODULE_ARGUMENTS: {}},
#                                  co.STEP_TYPE: co.STEP_TYPE_WORKER_EXECUTE, co.ACK_QUEUE: "queue"})
#
#     def test__validate_error(self):
#         with self.assertRaises(SchemaError):
#             self.task_obj._validate({})
#
#     @patch("cryton.worker.task.Task._run_in_process")
#     def test__execute_on_worker(self, mock_run_in_process):
#         mock_run_in_process.return_value = {"return_code": 0}
#         result = self.task_obj._execute({co.ACK_QUEUE: "test_que",
#                                          co.STEP_TYPE: co.STEP_TYPE_WORKER_EXECUTE,
#                                          co.ARGUMENTS: {
#                                              co.MODULE: "test_module",
#                                              co.MODULE_ARGUMENTS: {}
#                                          }})
#         self.assertEqual(result, {"return_code": 0})
#
#     @patch("cryton.worker.empire.EmpireClient.execute_on_agent")
#     def test__execute_on_agent(self, mock_execute_on_agent):
#         mock_execute_on_agent.return_value = 0
#         result = self.task_obj._execute({co.ACK_QUEUE: "test_que",
#                                          co.STEP_TYPE: co.STEP_TYPE_EMPIRE_EXECUTE,
#                                          co.ARGUMENTS: {
#                                              co.USE_AGENT: "test_agent",
#                                              co.MODULE: "test_module"
#                                          }})
#         self.assertEqual(result, 0)
#
#
# @patch('cryton.worker.util.logger.logger', logger.structlog.getLogger("cryton-worker-test"))
# class TestControlTask(TestCase):
#     @patch("cryton.worker.task.Process", Mock())
#     def setUp(self):
#         self.mock_main_queue = Mock()
#         self.message = Mock()
#         self.connection = Mock()
#         self.task_obj = task.ControlTask(self.message, self.mock_main_queue, self.connection)
#
#     def test__validate(self):
#         self.task_obj._validate({co.EVENT_T: "name", co.EVENT_V: {}})
#
#     def test__validate_error(self):
#         with self.assertRaises(SchemaError):
#             self.task_obj._validate({})
#
#     @patch("cryton.worker.event.Event.list_modules")
#     def test__execute(self, mock_list):
#         mock_list.return_value = 0
#         result = self.task_obj._execute({co.EVENT_T: co.EVENT_LIST_MODULES, co.EVENT_V: ""})
#         self.assertEqual(result, {co.EVENT_T: co.EVENT_LIST_MODULES, co.EVENT_V: 0})
#
#     def test__execute_unknown_event(self):
#         event_type = "UNKNOWN"
#         result = self.task_obj._execute({co.EVENT_T: event_type, co.EVENT_V: ""})
#         self.assertEqual(result, {co.EVENT_T: event_type, co.EVENT_V: {
#             co.RETURN_CODE: co.CODE_ERROR, co.OUTPUT: f"Unknown event type: {event_type}."}})
#
#     @patch("cryton.worker.event.Event.list_modules")
#     def test__execute_error(self, mock_list):
#         mock_list.side_effect = Exception
#         result = self.task_obj._execute({co.EVENT_T: co.EVENT_LIST_MODULES, co.EVENT_V: ""})
#         self.assertEqual(result.get(co.EVENT_T), co.EVENT_LIST_MODULES)
#         self.assertIsNotNone(result.get(co.EVENT_V).get(co.OUTPUT))

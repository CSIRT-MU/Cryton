# from unittest import TestCase
# from unittest.mock import patch, Mock
#
# from cryton.worker import event
# from cryton.worker.util import constants as co
#
#
# class TestEvent(TestCase):
#     def setUp(self):
#         self.mock_main_queue = Mock()
#         self.mock__response_pipe = Mock()
#         self.mock__request_pipe = Mock()
#
#         with patch("cryton.worker.event.Pipe") as mocked_pipe:
#             mocked_pipe.return_value = self.mock__response_pipe, self.mock__request_pipe
#             self.event_obj = event.Event({}, self.mock_main_queue)
#
#     @patch("cryton.worker.util.util.validate_module")
#     def test_validate_module(self, mock_validate):
#         mock_validate.return_value = {co.RETURN_CODE: co.CODE_OK}
#         result = self.event_obj.validate_module()
#         self.assertEqual({co.RETURN_CODE: co.CODE_OK}, result)
#
#     @patch("cryton.worker.util.util.list_modules")
#     def test_list_modules(self, mock_list_modules):
#         module_list = ["mod"]
#         mock_list_modules.return_value = module_list
#         result = self.event_obj.list_modules()
#         self.assertEqual({co.MODULE_LIST: module_list}, result)
#
#     @patch("cryton.worker.util.util.Metasploit")
#     def test_list_sessions(self, mock_msf):
#         session_list = ["session"]
#         mock_msf.return_value.is_connected.return_value = True
#         mock_msf.return_value.get_sessions.return_value = session_list
#         result = self.event_obj.list_sessions()
#         self.assertEqual({co.SESSION_LIST: session_list}, result)
#
#     @patch("cryton.worker.util.util.Metasploit")
#     def test_list_sessions_unconnected(self, mock_msf):
#         session_list = ["session"]
#         mock_msf.return_value.is_connected.return_value = False
#         mock_msf.return_value.error = Exception
#         result = self.event_obj.list_sessions()
#         self.assertEqual({co.SESSION_LIST: [], co.OUTPUT: str(Exception)}, result)
#
#     def test_stop_step_execution(self):
#         self.mock__response_pipe.recv.return_value = {co.RETURN_CODE: co.CODE_OK}
#         result = self.event_obj.stop_step_execution()
#         self.assertEqual({co.RETURN_CODE: co.CODE_OK}, result)
#
#     def test_health_check(self):
#         result = self.event_obj.health_check()
#         self.assertEqual({co.RETURN_CODE: co.CODE_OK}, result)
#
#     def test_add_trigger(self):
#         self.mock__response_pipe.recv.return_value = {co.RETURN_CODE: co.CODE_OK}
#         result = self.event_obj.add_trigger()
#         self.assertEqual({co.RETURN_CODE: co.CODE_OK}, result)
#
#     def test_remove_trigger(self):
#         self.mock__response_pipe.recv.return_value = {co.RETURN_CODE: co.CODE_OK}
#         result = self.event_obj.remove_trigger()
#         self.assertEqual({co.RETURN_CODE: co.CODE_OK}, result)
#
#     def test_list_triggers(self):
#         self.mock__response_pipe.recv.return_value = {co.RETURN_CODE: co.CODE_OK}
#         result = self.event_obj.list_triggers()
#         self.assertEqual({co.RETURN_CODE: co.CODE_OK}, result)

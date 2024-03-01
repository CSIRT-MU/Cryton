# from unittest import TestCase
# from unittest.mock import patch, Mock, MagicMock
#
# import os
# import subprocess
#
# from cryton.worker.util import util, module_util, exceptions, constants
#
#
# class TestUtil(TestCase):
#     @patch("cryton.worker.util.util.import_module")
#     def test_execute_cryton_module(self, mock_import):
#         mock_import.return_value.execute.return_value = {"return_code": 0}
#         mock_request_pipe = Mock()
#
#         util.run_attack_module("test", {"test": "test"}, mock_request_pipe)
#         mock_request_pipe.send.assert_called_once()
#         # self.assertEqual({"return_code": 0}, ret)
#
#     @patch("cryton.worker.util.util.import_module")
#     def test_execute_module_import_err(self, mock_import):
#         mock_import.side_effect = ModuleNotFoundError
#         mock_request_pipe = Mock()
#
#         util.run_attack_module("test", {"test": "test"}, mock_request_pipe)
#         mock_request_pipe.send.assert_called_once()
#         # self.assertEqual(-2, ret.get("return_code"))
#
#     @patch("cryton.worker.util.util.import_module")
#     def test_execute_module_call_err(self, mock_import):
#         mock_import.return_value.execute.side_effect = RuntimeError
#         mock_request_pipe = Mock()
#
#         util.run_attack_module("test", {"test": "test"}, mock_request_pipe)
#         mock_request_pipe.send.assert_called_once()
#         # self.assertEqual(-2, ret.get("return_code"))
#
#     @patch("cryton.worker.util.util.import_module")
#     def test_execute_module_attribute_err(self, mock_import):
#         mock_import.return_value.__delattr__("execute")
#         mock_request_pipe = Mock()
#
#         util.run_attack_module("test", {"test": "test"}, mock_request_pipe)
#         mock_request_pipe.send.assert_called_once()
#         # self.assertEqual(-2, ret.get("return_code"))
#
#     @patch("cryton.worker.util.util.import_module")
#     def test_validate_module(self, mock_import):
#         mock_import.return_value.validate.return_value = 0
#
#         ret = util.validate_module("test", {"test": "test"})
#         self.assertEqual(0, ret.get("return_code"))
#
#     @patch("cryton.worker.util.util.import_module")
#     def test_validate_module_import_err(self, mock_import):
#         mock_import.side_effect = ModuleNotFoundError
#
#         ret = util.validate_module("test", {"test": "test"})
#         self.assertEqual(-2, ret.get("return_code"))
#
#     @patch("cryton.worker.util.util.import_module")
#     def test_validate_module_call_err(self, mock_import):
#         mock_import.return_value.validate.side_effect = RuntimeError
#
#         ret = util.validate_module("test", {"test": "test"})
#         self.assertEqual(-2, ret.get("return_code"))
#
#     @patch("cryton.worker.util.util.import_module")
#     def test_validate_module_attribute_err(self, mock_import: Mock):
#         mock_import.return_value.__delattr__("validate")
#
#         ret = util.validate_module("test", {"test": "test"})
#         self.assertEqual(-2, ret.get("return_code"))
#
#     @patch("importlib.util")
#     def test_import_module(self, mock_import):
#         util.import_module("test")
#         mock_import.module_from_spec.assert_called()
#
#     @patch("importlib.util")
#     def test_import_module_missing_module(self, mock_import):
#         mock_import.module_from_spec.side_effect = ModuleNotFoundError
#
#         with self.assertRaises(ModuleNotFoundError):
#             util.import_module("test")
#
#     @patch("cryton_worker.etc.config.MODULES_DIRECTORY", "/tmp/mods4a4a5a7")
#     def test_list_modules(self):
#         ret = util.list_modules()
#         self.assertEqual([], ret)
#
#     @patch("cryton.worker.util.util.os.walk")
#     def test_install_modules_requirements(self, mock_walk):
#         mock_subprocess = subprocess
#         mock_subprocess.check_call = Mock()
#         mock_walk.return_value = [(".", ".", ["requirements.txt"])]
#
#         util.install_modules_requirements()
#         mock_subprocess.check_call.assert_called_once()
#
#     def test_create_prioritized_item(self):
#         item = {}
#         priority = 0
#         timestamp = 1
#         item_obj = util.PrioritizedItem(priority, item, timestamp)
#         self.assertEqual((priority, item, timestamp), (item_obj.priority, item_obj.item, item_obj.timestamp))
#
#     @patch("cryton.worker.util.util.paramiko.SSHClient")
#     def test_ssh_to_target(self, mock_client):
#         mock_connect = Mock()
#         mock_client.return_value.connect = mock_connect
#         ssh_arguments_key = {"target": "test_target", "username": "test_username", "ssh_key": "test_key", "port": 22}
#         ssh_arguments_password = {"target": "test_target", "username": "test_username", "password": "test_password",
#                                   "port": 22}
#
#         ret = util.ssh_to_target(ssh_arguments_key)
#         mock_connect.assert_called_with("test_target", username="test_username", key_filename="test_key", port=22,
#                                         timeout=10)
#         self.assertIsNotNone(ret)
#         ret = util.ssh_to_target(ssh_arguments_password)
#         mock_connect.assert_called_with("test_target", username="test_username", password="test_password", port=22,
#                                         timeout=10)
#         self.assertIsNotNone(ret)
#
#
# class TestMetasploit(TestCase):
#     @patch("cryton.worker.util.util.MsfRpcClient")
#     def setUp(self, mock_msf_client) -> None:
#         self.mock_client = mock_msf_client
#         self.msf = util.Metasploit()
#
#     @patch("cryton.worker.util.util.MsfRpcClient")
#     def test_get_client_error(self, mock_msf_client):
#         mock_msf_client.side_effect = Exception
#         result = util.Metasploit()
#         self.assertIsNotNone(result.error)
#
#     @patch("cryton.worker.util.util.MsfRpcClient")
#     def test_get_client(self, mock_client):
#         mock_client.return_value = Mock()
#         result = util.Metasploit()
#         self.assertIsNone(result.error)
#
#     def test_is_connected(self):
#         self.msf.error = None
#         self.assertTrue(self.msf.is_connected())
#
#     def test_is_not_connected(self):
#         self.msf.error = Exception
#         self.assertFalse(self.msf.is_connected())
#
#     def test_get_sessions(self):
#         self.mock_client.return_value.sessions.list = {"7": {"a": "ab", "b": "ab"}}
#         ret = self.msf.get_sessions(**{"a": "b", "b": "ab"})
#         self.assertEqual(["7"], ret)
#
#     def test_get_sessions_fail(self):
#         self.mock_client.return_value.sessions.list = {"7": {"a": "ab", "b": "ab"}}
#         ret = self.msf.get_sessions(**{"a": "c", "b": "ab"})
#         self.assertEqual([], ret)
#
#     @patch("pymetasploit3.msfrpc.ShellSession")
#     @patch("time.sleep", Mock())
#     def test_execute_in_session(self, shell_session_mock):
#         self.mock_client.return_value.sessions.session.return_value = shell_session_mock
#         shell_session_mock.read.side_effect = ["data_in_buffer", ""]
#         self.msf.read_shell_output = Mock(return_value="command_output")
#         result = self.msf.execute_in_session("command", "session_id", close=True)
#
#         shell_session_mock.write.assert_called_once_with("command")
#         self.assertEqual(result, "command_output")
#         shell_session_mock.stop.assert_called_once()
#         self.assertEqual(shell_session_mock.read.call_count, 2)
#
#     @patch("pymetasploit3.msfrpc.ShellSession")
#     @patch("time.sleep", Mock())
#     def test_execute_in_session_with_timeout(self, shell_session_mock):
#         self.mock_client.return_value.sessions.session.return_value = shell_session_mock
#         shell_session_mock.read.return_value = ""
#         self.msf.read_shell_output = Mock(return_value="command_output")
#         result = self.msf.execute_in_session("command", "session_id", 2)
#
#         shell_session_mock.write.assert_called_once_with("command")
#         self.assertEqual(result, "command_output")
#
#     @patch("pymetasploit3.msfrpc.ShellSession")
#     @patch("time.sleep", Mock())
#     def test_execute_in_session_check_end(self, shell_session_mock):
#         self.mock_client.return_value.sessions.session.return_value = shell_session_mock
#         shell_session_mock.read.return_value = ""
#         self.msf.execute_in_session("command", "session_id", None, ["check_end"], False)
#
#         shell_session_mock.run_with_output.assert_called_once_with(cmd="command", end_strs=["check_end"])
#         self.mock_client.return_value.sessions.session.assert_called_once_with("session_id")
#
#     @patch("pymetasploit3.msfrpc.ShellSession")
#     @patch("time.sleep", Mock())
#     def test_read_shell_output(self, shell_session_mock):
#         self.mock_client.return_value.sessions.session.return_value = shell_session_mock
#         shell_session_mock.read.side_effect = ["final", "result", ""]
#         result = self.msf.read_shell_output("1", None, 0)
#
#         self.assertEqual(result, "finalresult")
#         self.assertEqual(shell_session_mock.read.call_count, 3)
#
#     @patch("time.time", Mock(side_effect=[1, 3]))
#     @patch("pymetasploit3.msfrpc.ShellSession")
#     @patch("time.sleep", Mock())
#     def test_read_shell_output_with_timeout(self, shell_session_mock):
#         self.mock_client.return_value.sessions.session.return_value = shell_session_mock
#         shell_session_mock.read.side_effect = ["first", "second"]
#         result = self.msf.read_shell_output("1", 1, 1)
#
#         self.assertEqual(result, "first")
#         self.assertEqual(shell_session_mock.read.call_count, 1)
#
#     @patch("time.time", Mock(side_effect=[1, 2, 3]))
#     @patch("pymetasploit3.msfrpc.ShellSession")
#     @patch("time.sleep", Mock())
#     def test_read_shell_output_with_minimal_execution_time(self, shell_session_mock):
#         self.mock_client.return_value.sessions.session.return_value = shell_session_mock
#         shell_session_mock.read.side_effect = ["", "second", ""]
#         result = self.msf.read_shell_output("1", minimal_execution_time=2)
#
#         self.assertEqual(result, "second")
#         self.assertEqual(shell_session_mock.read.call_count, 3)
#
#     def test_execute_exploit(self):
#         mock_exploit = Mock()
#         exploit_name = "test_exploit"
#         payload_name = "test_payload"
#         self.mock_client.return_value.modules.use.return_value = mock_exploit
#
#         with self.assertRaises(exceptions.MsfModuleNotFound):
#             self.msf.execute_exploit(exploit_name)
#
#         self.mock_client.return_value.modules.exploits = [exploit_name]
#         self.msf.execute_exploit(exploit_name, payload_name)
#
#         self.mock_client.return_value.modules.use.assert_any_call(constants.EXPLOIT, exploit_name)
#         self.mock_client.return_value.modules.use.assert_any_call(constants.PAYLOAD, payload_name)
#         mock_exploit.execute.assert_called_once()
#
#     def test_execute_auxiliary(self):
#         mock_auxiliary = Mock()
#         auxiliary_name = "test_auxiliary"
#         self.mock_client.return_value.modules.use.return_value = mock_auxiliary
#
#         with self.assertRaises(exceptions.MsfModuleNotFound):
#             self.msf.execute_auxiliary(auxiliary_name)
#
#         self.mock_client.return_value.modules.auxiliary = [auxiliary_name]
#         self.msf.execute_auxiliary(auxiliary_name)
#
#         self.mock_client.return_value.modules.use.assert_called_once_with(constants.AUXILIARY, auxiliary_name)
#         mock_auxiliary.execute.assert_called_once()
#
#     @patch("cryton.worker.util.util.MsfConsole")
#     @patch("cryton.worker.util.util.connection.Connection")
#     def test_execute_msf_module_with_output(self, mocked_pipe_connection, mock_msf_console):
#         module_name = "test_module"
#         payload_name = "test_payload"
#         mock_msf_object = MagicMock()
#         mock_response = MagicMock()
#
#         self.mock_client.return_value.consoles.console.return_value = mock_msf_console
#         self.mock_client.return_value.modules.use.return_value = mock_msf_object
#         mock_msf_console.run_module_with_output.return_value = mock_response
#
#         self.msf.execute_msf_module_with_output(mock_msf_console, module_name, constants.EXPLOIT, False,
#                                                 mocked_pipe_connection, {}, payload_name, {})
#
#         self.mock_client.return_value.modules.use.assert_any_call(constants.EXPLOIT, module_name)
#         self.mock_client.return_value.modules.use.assert_any_call(constants.PAYLOAD, payload_name)
#         mock_msf_console.run_module_with_output.assert_called_once_with(mock_msf_object, payload=mock_msf_object,
#                                                                         run_as_job=False)
#         mocked_pipe_connection.send.assert_called_once_with(mock_response)
#
#
# class TestModuleUtil(TestCase):
#     def test_get_file_binary(self):
#         tmp_file = "/tmp/test568425j4L.txt"
#         with open(tmp_file, "w") as f:
#             f.write("test")
#         ret = module_util.get_file_binary(tmp_file)
#         self.assertEqual(ret, b"test")
#         os.remove(tmp_file)
#
#     def test_file_validate_ok(self):
#         file_test = module_util.File()
#         test_variable = "test"
#         with patch("os.path.isfile", return_value=True):
#             ret = file_test.validate("test")
#             self.assertEqual(test_variable, ret)
#
#     def test_file_validate_fail(self):
#         file_test = module_util.File()
#         with patch("os.path.isfile", return_value=False):
#             with self.assertRaises(Exception):
#                 file_test.validate("test")
#
#     def test_file_validate_repr(self):
#         file_test = module_util.File()
#         self.assertEqual(file_test.__repr__(), "File()")
#
#     def test_file_validate_err(self):
#         file_test = module_util.File({"test": "test"})
#         with self.assertRaises(Exception):
#             file_test.validate("test")
#
#     def test_file_validate_init(self):
#         with self.assertRaises(TypeError):
#             module_util.File(test="")
#
#     def test_dir_validate_ok(self):
#         dir_test = module_util.Dir()
#         test_variable = "test"
#         with patch("os.path.isdir", return_value=True):
#             ret = dir_test.validate("test")
#             self.assertEqual(test_variable, ret)
#
#     def test_dir_validate_fail(self):
#         dir_test = module_util.Dir()
#         with patch("os.path.isdir", return_value=False):
#             with self.assertRaises(Exception):
#                 dir_test.validate("test")
#
#     def test_dir_validate_repr(self):
#         dir_test = module_util.Dir()
#         self.assertEqual(dir_test.__repr__(), "Dir()")
#
#     def test_dir_validate_err(self):
#         dir_test = module_util.Dir({"test": "test"})
#         with self.assertRaises(Exception):
#             dir_test.validate("test")
#
#     def test_dir_validate_init(self):
#         with self.assertRaises(TypeError):
#             module_util.Dir(test="")

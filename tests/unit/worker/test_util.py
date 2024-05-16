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

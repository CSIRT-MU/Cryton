# import subprocess
# from unittest.mock import MagicMock, patch
# import pytest
#
# from cryton.modules.medusa import mod
#
#
# @pytest.fixture
# def medusa_arguments():
#     return {
#         "target": "address", "credentials": {"username": "test", "password": "test"}, "raw_output": True
#     }
#
#
# @pytest.fixture
# def mock_subprocess_run(mocker):
#     mock_run = mocker.patch("subprocess.run")
#     mock_run.return_value.stdout.decode.return_value = "ACCOUNT FOUND: [ssh] Host: address User: testlogin " \
#                                                        "Password: testpass [SUCCESS]"
#     mock_run.return_value.stderr.decode.return_value = "test_error"
#     return mock_run
#
#
# @pytest.mark.parametrize(
#     "p_username, p_username_file, p_result",
#     [
#         ("test_username", None, ["-u", "test_username"]),
#         (None, "test_user_file", ["-U", "test_user_file"]),
#         (None, None, [])
#     ]
# )
# def test_parse_username(p_username, p_username_file, p_result):
#     result = mod.parse_username(p_username, p_username_file)
#     assert result == p_result
#
#
# @pytest.mark.parametrize(
#     "p_password, p_password_file, p_result",
#     [
#         ("test_password", None, ["-p", "test_password"]),
#         (None, "test_password_file", ["-P", "test_password_file"]),
#         (None, None, [])
#     ]
# )
# def test_parse_password(p_password, p_password_file, p_result, mocker):
#     result = mod.parse_password(p_password, p_password_file)
#     assert result == p_result
#
#
# def test_parse_credentials():
#     result = mod.parse_credentials("ACCOUNT FOUND: [ssh] Host: address User: testlogin Password: testpass [SUCCESS]")
#     assert result == {
#         "username": "testlogin",
#         "password": "testpass",
#         "all_credentials": [{"username": "testlogin", "password": "testpass"}]}
#
#
# @pytest.mark.parametrize(
#     "p_arguments, p_result",
#     [
#         ({"target": "test_target", "credentials": {"username": "test_username", "password": "test_password"}},
#          ["medusa", "-h", "test_target", "-t", "4", "-M", "ssh", "-u", "test_username", "-p", "test_password"]),
#         ({"target": "test_target", "credentials": {"combo_file": "test_combo_file"}},
#          ["medusa", "-h", "test_target", "-t", "4", "-M", "ssh", "-C", "test_combo_file"])
#     ]
# )
# def test_parse_command(mocker, p_arguments, p_result):
#     mocker.patch("mod.parse_username", return_value=["-u", "test_username"])
#     mocker.patch("mod.parse_password", return_value=["-p", "test_password"])
#
#     result = mod.parse_command(p_arguments)
#
#     assert result == p_result
#
# @pytest.mark.parametrize(
#     "p_arguments, p_result",
#     [
#         ({"target": "test_target", "credentials": {}},
#          ["medusa", "-h", "test_target", "-t", "4", "-M", "ssh"])
#     ]
# )
# def test_parse_command_without_username_password(mocker, p_arguments, p_result):
#     mocker.patch("mod.parse_username", return_value=[])
#     mocker.patch("mod.parse_password", return_value=[])
#
#     result = mod.parse_command(p_arguments)
#
#     assert result == p_result
#
# def test_execute_with_custom_command(mocker, mock_subprocess_run):
#     validate_mock = mocker.patch("mod.validate", MagicMock())
#     args = {"command": "medusa -t 4 -u testuser -p testpass -h address -M ssh"}
#
#     result = mod.execute(args)
#     validate_mock.assert_called_once_with(args)
#
#     assert result == {
#         "return_code": 0,
#         "output": "test_error",
#         "serialized_output": {
#             "username": "testlogin",
#             "password": "testpass",
#             "all_credentials": [{"username": "testlogin", "password": "testpass"}]
#         }
#     }
#
#
# def test_execute_with_arguments(mocker, mock_subprocess_run, medusa_arguments):
#     validate_mock = mocker.patch("mod.validate")
#     parse_command_mock = mocker.patch("mod.parse_command", return_value=["test_subprocess_result"])
#     parse_credentials_mock = mocker.patch("mod.parse_credentials", return_value={
#             "username": "testuser",
#             "password": "testpass",
#             "all_credentials": {"testuser": "testpass"}
#         })
#
#     result = mod.execute(medusa_arguments)
#     validate_mock.assert_called_once_with(medusa_arguments)
#     parse_command_mock.assert_called_once_with(medusa_arguments)
#     mock_subprocess_run.assert_called_once_with(["test_subprocess_result"], capture_output=True)
#     parse_credentials_mock.assert_called_once_with(
#         "ACCOUNT FOUND: [ssh] Host: address User: testlogin Password: testpass [SUCCESS]"
#     )
#
#     assert result == {
#         "return_code": 0,
#         "output": "ACCOUNT FOUND: [ssh] Host: address User: testlogin Password: testpass [SUCCESS] test_error",
#         "serialized_output": {
#             "username": "testuser",
#             "password": "testpass",
#             "all_credentials": {"testuser": "testpass"}
#         }
#     }
#
#
# def test_execute_exceptions(mocker, medusa_arguments):
#     mocker.patch("mod.validate")
#     with patch("mod.parse_command", side_effect=FileNotFoundError("test_error")):
#         result = mod.execute(medusa_arguments)
#         assert result == {
#             "return_code": -1,
#             "output": "test_error",
#             "serialized_output": {}
#         }
#
#     with patch("mod.subprocess.run", side_effect=FileNotFoundError("test_error")):
#         result = mod.execute(medusa_arguments)
#         assert result == {
#             "return_code": -1,
#             "output": "Check if your command starts with \"medusa\" and is installed. original error: test_error",
#             "serialized_output": {}
#         }
#
#     with patch("mod.subprocess.run", side_effect=subprocess.SubprocessError("test_error")):
#         result = mod.execute(medusa_arguments)
#         assert result == {
#             "return_code": -1,
#             "output": "Medusa couldn\'t start. original error: test_error",
#             "serialized_output": {}
#         }
#

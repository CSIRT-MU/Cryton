# import pytest
# from unittest.mock import Mock, patch
# from pytest_mock import MockerFixture
#
# from cryton.hive.utility import logger
# from cryton.hive.cryton_app.management.commands import runserver, startlistener, startgunicorn, start  # startmonitoring
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger('cryton-core-test'))
# class TestCommandRunServer:
#     path = "cryton.hive.cryton_app.management.commands.runserver"
#
#     @pytest.fixture
#     def f_logger_object(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".logger_object")
#
#     @pytest.fixture
#     def f_original_handle(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".CommandRunserver.handle")
#
#     @pytest.fixture
#     def f_thread(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".Thread")
#
#     def test_handle(self, f_original_handle, f_thread, f_logger_object):
#         runserver.Command().handle()
#
#         f_thread.return_value.start.assert_called_once()
#         f_original_handle.assert_called_once()
#         f_logger_object.log_queue.put.assert_called_once_with(None)
#
#     def test_handle_error(self, f_original_handle, f_thread, f_logger_object):
#         f_original_handle.side_effect = RuntimeError
#
#         with pytest.raises(RuntimeError):
#             runserver.Command().handle()
#
#         f_thread.return_value.start.assert_called_once()
#         f_original_handle.assert_called_once()
#         f_logger_object.log_queue.put.assert_called_once_with(None)
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger('cryton-core-test'))
# class TestCommandStartListener:
#     path = "cryton.hive.cryton_app.management.commands.startlistener"
#
#     def test_handle(self, mocker):
#         mock_listener: Mock = mocker.patch(self.path + ".Listener")
#
#         startlistener.Command().handle()
#         mock_listener.return_value.start.assert_called()
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger('cryton-core-test'))
# class TestCommandStartMonitoring:
#     path = "cryton.hive.cryton_app.management.commands.startmonitoring"
#
#     @pytest.mark.skip(reason="this feature is not available at the moment")
#     def test_handle(self, mocker):
#         pass
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger('cryton-core-test'))
# class TestStartGunicorn:
#     path = "cryton.hive.cryton_app.management.commands.startgunicorn"
#
#     @pytest.fixture
#     def f_logger_object(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".logger_object")
#
#     @pytest.fixture
#     def f_thread(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".Thread")
#
#     @pytest.fixture
#     def f_gunicorn_application(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".GunicornApplication")
#
#     def test_command_add_arguments(self):
#         mock_parser = Mock()
#
#         startgunicorn.Command().add_arguments(mock_parser)
#
#         assert mock_parser.add_argument.call_count == 2
#
#     def test_command_handle(self, f_gunicorn_application, f_thread, f_logger_object):
#         startgunicorn.Command().handle()
#
#         f_thread.return_value.start.assert_called_once()
#         f_gunicorn_application.return_value.run.assert_called_once()
#         f_logger_object.log_queue.put.assert_called_once_with(None)
#
#     def test_command_handle_error(self, f_gunicorn_application, f_thread, f_logger_object):
#         f_gunicorn_application.return_value.run.side_effect = RuntimeError
#
#         with pytest.raises(RuntimeError):
#             startgunicorn.Command().handle()
#
#         f_thread.return_value.start.assert_called_once()
#         f_gunicorn_application.return_value.run.assert_called_once()
#         f_logger_object.log_queue.put.assert_called_once_with(None)
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger('cryton-core-test'))
# class TestStart:
#     path = "cryton.hive.cryton_app.management.commands.start"
#
#     @pytest.fixture
#     def f_logger_object(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".logger_object")
#
#     @pytest.fixture
#     def f_thread(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".Thread")
#
#     @pytest.fixture
#     def f_gunicorn_application(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".GunicornApplication")
#
#     @pytest.fixture
#     def f_listener(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".Listener")
#
#     @pytest.fixture
#     def f_click_echo(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".echo")
#
#     @pytest.fixture
#     def f_click_secho(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".secho")
#
#     @pytest.fixture
#     def f_time_sleep(self, mocker: MockerFixture):
#         return mocker.patch("time.sleep")
#
#     def test_command_add_arguments(self):
#         mock_parser = Mock()
#
#         start.Command().add_arguments(mock_parser)
#
#         assert mock_parser.add_argument.call_count == 2
#
#     def test_command_handle(self, f_gunicorn_application, f_thread, f_logger_object, f_listener, f_click_echo,
#                             f_click_secho, f_time_sleep):
#         f_time_sleep.side_effect = KeyboardInterrupt
#
#         start.Command().handle()
#
#         f_gunicorn_application.return_value.start.assert_called_once()
#         f_listener.return_value.start.assert_called_once_with(False)
#         f_thread.return_value.start.assert_called_once()
#         f_gunicorn_application.return_value.stop.assert_called_once()
#         f_listener.return_value.stop.assert_called_once()
#         f_logger_object.log_queue.put.assert_called_once_with(None)
#         assert f_click_echo.call_count == 13
#         assert f_click_secho.call_count == 1

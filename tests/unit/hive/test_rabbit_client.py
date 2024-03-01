# import pytest
# from pytest_mock import MockerFixture
# from unittest.mock import patch, Mock
#
# from cryton.hive.utility import logger, constants, rabbit_client, exceptions
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger(constants.LOGGER_CRYTON_TESTING))
# class TestRpcClient:
#     path = "cryton.hive.utility.rabbit_client"
#
#     @pytest.fixture
#     def f_rpc_client(self, mocker: MockerFixture):
#         mocker.patch(self.path + ".RpcClient.open")
#         rpc_client = rabbit_client.RpcClient()
#
#         return rpc_client
#
#     def test___enter__(self, f_rpc_client):
#         result = f_rpc_client.__enter__()
#
#         assert result == f_rpc_client
#
#     def test___exit__(self, f_rpc_client):
#         mock_close = Mock()
#         f_rpc_client.close = mock_close
#
#         f_rpc_client.__exit__("", "", "")
#
#         mock_close.assert_called_once()
#
#     def test_open(self, mocker: MockerFixture):
#         # .open() is called in the __init__ method
#         mock_connection = mocker.patch(self.path + ".amqpstorm.Connection")
#
#         rpc_client = rabbit_client.RpcClient()
#
#         mock_connection.assert_called_once()
#         mock_connection.return_value.channel.assert_called_once()
#         mock_connection.return_value.channel.return_value.queue.declare.\
#             assert_called_once_with(rpc_client.callback_queue)
#         mock_connection.return_value.channel.return_value.basic.consume.\
#             assert_called_once_with(rpc_client._on_response, no_ack=True, queue=rpc_client.callback_queue)
#         assert rpc_client.channel is not None
#         assert rpc_client.connection is not None
#         assert rpc_client.callback_queue is not None
#
#     def test_open_with_channel(self, mocker: MockerFixture):
#         # .open() is called in the __init__ method
#         mock_connection = mocker.patch(self.path + ".amqpstorm.Connection")
#         mock_channel = Mock()
#
#         rpc_client = rabbit_client.RpcClient(mock_channel)
#
#         mock_connection.assert_not_called()
#         mock_connection.return_value.channel.assert_not_called()
#         mock_channel.queue.declare.assert_called_once_with(rpc_client.callback_queue)
#         mock_channel.basic.consume.assert_called_once_with(rpc_client._on_response, no_ack=True,
#                                                            queue=rpc_client.callback_queue)
#         assert rpc_client.channel is not None
#         assert rpc_client.connection is None
#         assert rpc_client.callback_queue is not None
#
#     def test_close(self, f_rpc_client):
#         mock_connection = Mock()
#         mock_channel = Mock()
#         f_rpc_client.channel = mock_channel
#         f_rpc_client.connection = mock_connection
#         f_rpc_client.callback_queue = "queue"
#
#         f_rpc_client.close()
#
#         mock_channel.queue.delete.assert_called_once_with("queue")
#         mock_channel.close.assert_called_once()
#         mock_connection.close.assert_called_once()
#
#     def test_close_no_created_connection(self, f_rpc_client):
#         mock_channel = Mock()
#         f_rpc_client.channel = mock_channel
#         f_rpc_client.callback_queue = "queue"
#
#         f_rpc_client.close()
#
#         mock_channel.queue.delete.assert_called_once_with("queue")
#         mock_channel.close.assert_not_called()
#
#     def test_call(self, f_rpc_client):
#         f_rpc_client.response = "response"
#
#         mock_channel = Mock()
#         mock__create_message = Mock()
#         mock__clean_up = Mock()
#         mock__wait_for_response = Mock()
#         f_rpc_client._clean_up = mock__clean_up
#         f_rpc_client._create_message = mock__create_message
#         f_rpc_client._wait_for_response = mock__wait_for_response
#         f_rpc_client.channel = mock_channel
#
#         result = f_rpc_client.call("queue", {}, {}, "custom_queue")
#
#         mock__clean_up.assert_called_once()
#         mock_channel.queue.declare.assert_called_once_with("queue")
#         mock__create_message.assert_called_once_with({}, {}, "custom_queue")
#         mock__create_message.return_value.publish.assert_called_once_with("queue")
#         mock__wait_for_response.assert_called_once()
#         assert result == "response"
#
#     def test__clean_up(self, f_rpc_client):
#         f_rpc_client.response = "response"
#         f_rpc_client.correlation_id = "id"
#
#         f_rpc_client._clean_up()
#
#         assert f_rpc_client.response is None
#         assert f_rpc_client.correlation_id is None
#
#     def test__create_message(self, f_rpc_client, mocker: MockerFixture):
#         f_rpc_client.callback_queue = "queue"
#
#         mock_message_create = mocker.patch(self.path + ".amqpstorm.Message.create")
#         mock_channel = Mock()
#         f_rpc_client.channel = mock_channel
#
#         result = f_rpc_client._create_message({}, {})
#
#         mock_message_create.assert_called_once_with(mock_channel, "{}", {})
#         assert result == mock_message_create.return_value
#         assert result.reply_to == "queue"
#         assert f_rpc_client.correlation_id == mock_message_create.return_value.correlation_id
#
#     def test__create_message_with_custom_queue(self, f_rpc_client, mocker: MockerFixture):
#         f_rpc_client.callback_queue = "queue"
#
#         mock_message_create = mocker.patch(self.path + ".amqpstorm.Message.create")
#         mock_channel = Mock()
#         f_rpc_client.channel = mock_channel
#
#         result = f_rpc_client._create_message({}, {}, "custom_queue")
#
#         mock_message_create.assert_called_once_with(mock_channel, "{\"ack_queue\": \"queue\"}", {})
#         assert result == mock_message_create.return_value
#         assert result.reply_to == "custom_queue"
#         assert f_rpc_client.correlation_id == mock_message_create.return_value.correlation_id
#
#     def test__wait_for_response(self, f_rpc_client):
#         def update_response():
#             f_rpc_client.response = "response"
#
#         mock_channel = Mock()
#         mock_channel.process_data_events.side_effect = update_response
#         f_rpc_client.channel = mock_channel
#
#         f_rpc_client._wait_for_response()
#
#         mock_channel.process_data_events.assert_called_once()
#         assert f_rpc_client.response == "response"
#
#     def test__wait_for_response_timeout(self, f_rpc_client, mocker: MockerFixture, caplog):
#         mock_channel = Mock()
#         f_rpc_client.channel = mock_channel
#
#         mock_time_time = mocker.patch(self.path + ".time.time")
#         mock_time_time.side_effect = [0, 0, 0, 99999, 0]  # Logs use time.time(), that's the reason for other zeros
#
#         with pytest.raises(exceptions.RpcTimeoutError):
#             f_rpc_client._wait_for_response()
#
#         mock_channel.process_data_events.assert_called_once()
#         assert f_rpc_client.response is None
#         assert "Couldn't get response in time." in caplog.text
#
#     def test__on_response(self, f_rpc_client, caplog):
#         f_rpc_client.correlation_id = "id"
#
#         mock_message = Mock()
#         mock_message.correlation_id = "id"
#
#         f_rpc_client._on_response(mock_message)
#
#         mock_message.json.assert_called_once()
#         assert f_rpc_client.response == mock_message.json.return_value
#         assert "Received a message with an unknown correlation_id." not in caplog.text
#
#     def test__on_response_unknown_correlation_id(self, f_rpc_client, caplog):
#         f_rpc_client.correlation_id = "id"
#
#         mock_message = Mock()
#         mock_message.correlation_id = "unknown_id"
#
#         f_rpc_client._on_response(mock_message)
#
#         mock_message.json.assert_not_called()
#         assert f_rpc_client.response is None
#         assert "Received message with an unknown correlation_id." in caplog.text
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger(constants.LOGGER_CRYTON_TESTING))
# class TestClient:
#     path = "cryton.hive.utility.rabbit_client"
#
#     @pytest.fixture
#     def f_client(self, mocker: MockerFixture):
#         mocker.patch(self.path + ".Client.open")
#         client = rabbit_client.Client()
#
#         return client
#
#     def test___enter__(self, f_client):
#         result = f_client.__enter__()
#
#         assert result == f_client
#
#     def test___exit__(self, f_client):
#         mock_close = Mock()
#         f_client.close = mock_close
#
#         f_client.__exit__("", "", "")
#
#         mock_close.assert_called_once()
#
#     def test_open(self, mocker: MockerFixture):
#         # .open() is called in the __init__ method
#         mock_connection = mocker.patch(self.path + ".amqpstorm.Connection")
#
#         client = rabbit_client.Client()
#
#         mock_connection.assert_called_once()
#         mock_connection.return_value.channel.assert_called_once()
#         assert client.channel is not None
#         assert client.connection is not None
#
#     def test_open_with_channel(self, mocker: MockerFixture):
#         # .open() is called in the __init__ method
#         mock_connection = mocker.patch(self.path + ".amqpstorm.Connection")
#         mock_channel = Mock()
#
#         client = rabbit_client.Client(mock_channel)
#
#         mock_connection.assert_not_called()
#         mock_connection.return_value.channel.assert_not_called()
#
#         assert client.channel is not None
#         assert client.connection is None
#
#     def test_close(self, f_client):
#         mock_connection = Mock()
#         mock_channel = Mock()
#         f_client.channel = mock_channel
#         f_client.connection = mock_connection
#
#         f_client.close()
#
#         mock_channel.close.assert_called_once()
#         mock_connection.close.assert_called_once()
#
#     def test_close_no_created_connection(self, f_client):
#         mock_channel = Mock()
#         f_client.channel = mock_channel
#
#         f_client.close()
#
#         mock_channel.close.assert_not_called()
#
#     def test_send_message(self, f_client, mocker: MockerFixture):
#         mock_channel = Mock()
#         f_client.channel = mock_channel
#
#         mock_message_create = mocker.patch(self.path + ".amqpstorm.Message.create")
#
#         f_client.send_message("queue", {}, {})
#
#         mock_channel.queue.declare.assert_called_once_with("queue")
#         mock_message_create.assert_called_once_with(mock_channel, "{}", {})
#         mock_message_create.return_value.publish.assert_called_once_with("queue")

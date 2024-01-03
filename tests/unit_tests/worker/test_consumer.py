import pytest
from unittest import TestCase
from unittest.mock import patch, Mock

from cryton_worker.lib import consumer, task
from cryton_worker.lib.util import logger
import amqpstorm


@patch('cryton_worker.lib.util.logger.logger', logger.structlog.getLogger("cryton-worker-test"))
class TestChannelConsumer:
    path = "cryton_worker.lib.consumer"

    @pytest.fixture
    def f_channel_consumer(self):
        channel_consumer = consumer.ChannelConsumer(1, Mock(), {"queue": "callback"})

        return channel_consumer

    def test___init__(self):
        mock_channel = Mock()
        mock_connection = Mock()
        mock_connection.channel.return_value = mock_channel

        result = consumer.ChannelConsumer(1, mock_connection, {"queue": "callback"})

        mock_connection.channel.assert_called_once()
        mock_channel.basic.qos.assert_called_once_with(1)
        mock_channel.queue.declare.assert_called_once_with("queue")
        mock_channel.basic.consume.assert_called_once_with("callback", "queue")
        assert result._id == 1
        assert result._channel == mock_channel

    def test__channel_consumer_connection_error(self, f_channel_consumer, caplog):
        mock_channel = Mock()
        mock_channel.is_closed = False
        mock_channel.start_consuming.side_effect = amqpstorm.AMQPConnectionError
        f_channel_consumer._channel = mock_channel

        f_channel_consumer.start()

        mock_channel.start_consuming.assert_called_once()
        # TODO: caplog is not working for some reason, fix with logging rework
        # assert "Channel consumer encountered a connection error." in caplog.text
        # assert len(caplog.records) == 3

    def test__channel_consumer_unknown_error(self, f_channel_consumer, caplog):
        mock_channel = Mock()

        def close_channel():
            mock_channel.is_closed = True
            raise ValueError

        mock_channel.is_closed = False
        mock_channel.start_consuming.side_effect = close_channel
        f_channel_consumer._channel = mock_channel

        f_channel_consumer.start()

        mock_channel.start_consuming.assert_called_once()
        # TODO: caplog is not working for some reason, fix with logging rework
        # assert "Channel consumer encountered an error." in caplog.text
        # assert len(caplog.records) == 3


@patch("cryton_worker.lib.util.logger.logger", logger.structlog.getLogger("cryton-worker-debug"))
class TestConsumer(TestCase):
    def setUp(self):
        self.mock_main_queue = Mock()
        self.consumer_obj = consumer.Consumer(self.mock_main_queue, "host", 1, "user", "pass", "prefix", 3, 3, False)
        self.consumer_obj._main_queue = Mock()

    def test_init_wrong_consumers(self):
        consumer_obj = consumer.Consumer(self.mock_main_queue, "host", 1, "user", "pass", "prefix", 0, 3, False)
        self.assertEqual(consumer_obj._channel_consumer_count, 1)

    def test___str__(self):
        result = str(self.consumer_obj)
        self.assertEqual(result, "user@host:1")

    @patch("cryton_worker.lib.consumer.Consumer._update_connection", Mock())
    @patch("cryton_worker.lib.consumer.Consumer._start_channel_consumers", Mock())
    @patch("cryton_worker.lib.worker.time.sleep")
    def test_start(self, mock_sleep):
        mock_sleep.side_effect = amqpstorm.AMQPConnectionError
        self.consumer_obj.start()

    @patch("cryton_worker.lib.consumer.Consumer._update_connection")
    @patch("cryton_worker.lib.consumer.Consumer._start_channel_consumers", Mock())
    @patch("cryton_worker.lib.worker.time.sleep")
    def test_start_persistent(self, mock_sleep, mock_update_connection):
        mock_update_connection.side_effect = [False, RuntimeError]
        mock_sleep.side_effect = amqpstorm.AMQPConnectionError
        self.consumer_obj._persistent = True
        with self.assertLogs("cryton-worker-debug", level="DEBUG") as cm:
            with self.assertRaises(RuntimeError):
                self.consumer_obj.start()
        self.assertIn("Ignoring connection error due to persistent mode.", cm.output[1])

    @patch("time.sleep")
    def test_stop(self, mock_time):
        mock_task = Mock()
        mock_time.side_effect = KeyboardInterrupt
        mock_connection, mock_channel = Mock(), Mock()
        mock_connection.channels = {1: mock_channel}

        self.consumer_obj._connection = mock_connection
        self.consumer_obj._tasks.append(Mock())
        self.consumer_obj._tasks.append(mock_task)

        self.consumer_obj.stop()
        mock_task.kill.assert_called_once()
        mock_connection.close.assert_called_once()
        mock_channel.close.assert_called_once()

    @patch("cryton_worker.lib.consumer.Consumer._create_connection")
    def test__update_connection_is_none(self, mock_create_conn: Mock):
        result = self.consumer_obj._update_connection()
        self.assertTrue(result)
        mock_create_conn.assert_called_once()

    def test__update_connection_is_ok(self):
        self.consumer_obj._connection = Mock()
        self.consumer_obj._connection.is_open = True
        result = self.consumer_obj._update_connection()
        self.assertFalse(result)

    @patch("cryton_worker.lib.consumer.Consumer._create_connection", Mock())
    def test__update_connection_is_closed(self):
        self.consumer_obj._connection = Mock()
        self.consumer_obj._connection.is_open = False
        result = self.consumer_obj._update_connection()
        self.assertTrue(result)

    @patch("threading.Thread", Mock())
    @patch("threading.Thread.start")
    @patch("cryton_worker.lib.consumer.ChannelConsumer")
    def test__start_channel_consumers(self, mock_channel_consumer, mock_start):
        self.consumer_obj._start_channel_consumers()
        mock_channel_consumer.assert_called()
        mock_start.assert_called()

    @patch("cryton_worker.lib.task.AttackTask")
    def test__callback_attack(self, mock_task):
        self.consumer_obj._callback_attack(Mock())
        self.assertNotEqual([], self.consumer_obj._tasks)
        mock_task.return_value.start.assert_called()

    @patch("cryton_worker.lib.task.ControlTask")
    def test__callback_control(self, mock_task):
        self.consumer_obj._callback_control(Mock())
        self.assertNotEqual([], self.consumer_obj._tasks)
        mock_task.return_value.start.assert_called()

    @patch("cryton_worker.lib.task.AgentTask")
    def test__callback_agent(self, mock_task):
        self.consumer_obj._callback_agent(Mock())
        self.assertNotEqual([], self.consumer_obj._tasks)
        mock_task.return_value.start.assert_called()

    @patch("time.sleep", Mock())
    @patch("amqpstorm.Connection")
    def test__create_connection(self, mock_conn: Mock):
        self.consumer_obj._create_connection()
        mock_conn.assert_called_once()
        mock_conn.side_effect = amqpstorm.AMQPError
        with self.assertRaises(amqpstorm.AMQPConnectionError):
            self.consumer_obj._create_connection()

    def test__create_connection_stopped(self):
        self.consumer_obj.is_running = Mock(return_value=False)
        self.assertIsNone(self.consumer_obj._create_connection())

    @patch("amqpstorm.Message.create")
    def test_send_message(self, mock_create):
        mock_connection, mock_channel = Mock(), Mock()
        mock_connection.channel.return_value = mock_channel
        self.consumer_obj._connection = mock_connection
        self.consumer_obj.send_message("", {}, {})
        mock_create.assert_called_once()

    def test_send_message_fail(self):
        mock_connection = Mock()
        mock_connection.channel.side_effect = amqpstorm.AMQPError
        self.consumer_obj._connection = mock_connection
        self.consumer_obj.send_message("", {}, {})

        assert len(self.consumer_obj._undelivered_messages) == 1

    def test__redelivered_messages(self):
        mock_send_message = Mock()

        self.consumer_obj._undelivered_messages = [Mock()]
        self.consumer_obj.send_message = mock_send_message

        self.consumer_obj._redelivered_messages()

        mock_send_message.assert_called_once()
        assert not self.consumer_obj._undelivered_messages

    def test__get_undelivered_task_replies(self):
        mock_message = Mock()
        mock_task = Mock(spec=task.Task)
        mock_task.undelivered_messages = [mock_message]

        self.consumer_obj._tasks = [mock_task]
        self.consumer_obj._get_undelivered_task_replies()

        assert self.consumer_obj._undelivered_messages == [mock_message]

    def test_pop_task(self):
        mock_task = Mock()
        mock_task.correlation_id = "id"
        self.consumer_obj._tasks.append(mock_task)
        result = self.consumer_obj.pop_task("id")
        self.assertEqual(result, mock_task)

    def test_pop_task_not_found(self):
        self.assertIsNone(self.consumer_obj.pop_task("id"))

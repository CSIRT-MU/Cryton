from unittest import TestCase
from unittest.mock import patch, Mock

from cryton.worker import worker
from cryton.worker.utility import constants as co, logger, util, exceptions


@patch("cryton.worker.utility.logger.logger", logger.structlog.getLogger("cryton-worker-debug"))
class TestWorker(TestCase):
    def setUp(self):
        self.mock_main_queue = Mock()
        self.worker_obj = worker.Worker("host", 1, "user", "pass", "prefix", 3, 3, 3, False)
        self.worker_obj._main_queue = self.mock_main_queue

    def test_init_wrong_consumers(self):
        worker_obj = worker.Worker("host", 1, "user", "pass", "prefix", 3, 0, 3, False)
        self.assertEqual(worker_obj._processor_count, 1)

    @patch("cryton.worker.worker.Worker._start_consumer", Mock())
    @patch("cryton.worker.worker.Worker._start_threaded_processors", Mock())
    @patch("cryton.worker.worker.Worker.stop")
    @patch("cryton.worker.worker.time.sleep")
    @patch("cryton.worker.worker.MetasploitClientUpdated", Mock())
    def test_start(self, mock_sleep, mock_stop):
        mock_sleep.side_effect = KeyboardInterrupt
        self.worker_obj.start()
        mock_stop.assert_called_once()

    @patch("cryton.worker.worker.Worker._stop_threaded_processors", Mock())
    @patch("cryton.worker.worker.Worker._remove_trigger", Mock())
    @patch("cryton.worker.consumer.Consumer.stop", Mock())
    def test_stop(self):
        self.worker_obj.stop()
        self.assertTrue(self.worker_obj._stopped)

    @patch("threading.Thread", Mock())
    @patch("threading.Thread.start")
    def test__start_threaded_processors(self, mock_start):
        self.worker_obj._start_threaded_processors()
        mock_start.assert_called()

    def test__stop_threaded_processors(self):
        self.worker_obj._stop_threaded_processors()
        self.mock_main_queue.put.assert_called()

    @patch("threading.Thread", Mock())
    @patch("threading.Thread.start")
    def test__start_consumer(self, mock_start):
        self.worker_obj._start_consumer()
        mock_start.assert_called()

    def test__threaded_processor_action_shutdown(self):
        self.mock_main_queue.get.side_effect = [
            util.PrioritizedItem(0, {co.ACTION: co.ACTION_SHUTDOWN_THREADED_PROCESSOR})
        ]
        self.worker_obj._threaded_processor(1)

    def test__threaded_processor_action_unknown(self):
        self.mock_main_queue.get.side_effect = [
            util.PrioritizedItem(0, {co.ACTION: "UNKNOWN"}),
            util.PrioritizedItem(0, {co.ACTION: co.ACTION_SHUTDOWN_THREADED_PROCESSOR})
        ]
        with self.assertLogs("cryton-worker-debug", level="WARNING") as cm:
            self.worker_obj._threaded_processor(1)
        self.assertIn("Request contains unknown action.", cm.output[0])

    def test__threaded_processor_empty_action(self):
        self.mock_main_queue.get.side_effect = [
            util.PrioritizedItem(0, {}),
            util.PrioritizedItem(0, {co.ACTION: co.ACTION_SHUTDOWN_THREADED_PROCESSOR})
        ]
        with self.assertLogs("cryton-worker-debug", level="WARNING") as cm:
            self.worker_obj._threaded_processor(1)
        self.assertIn("Request doesn't contain action.", cm.output[0])

    @patch("cryton.worker.worker.Worker._stop_threaded_processors")
    def test__threaded_processor_action_exception(self, mock_action):
        self.mock_main_queue.get.side_effect = [
            util.PrioritizedItem(0, {co.ACTION: co.ACTION_SEND_MESSAGE}),
            util.PrioritizedItem(0, {co.ACTION: co.ACTION_SHUTDOWN_THREADED_PROCESSOR})
        ]
        mock_action.side_effect = RuntimeError
        with self.assertLogs("cryton-worker-debug", level="WARNING") as cm:
            self.worker_obj._threaded_processor(1)
        self.assertIn("Request threw an exception in the process.", cm.output[0])

    @patch("cryton.worker.consumer.Consumer.pop_task")
    def test__kill_task(self, mock_pop_task):
        mock_task = Mock()
        mock_pipe = Mock()
        mock_pop_task.return_value = mock_task

        self.worker_obj._kill_task({co.RESULT_PIPE: mock_pipe, co.CORRELATION_ID: "1"})

        mock_pipe.send.assert_called_once_with({co.RESULT: co.CODE_OK})

    @patch("cryton.worker.consumer.Consumer.pop_task")
    def test__kill_task_error(self, mock_pop_task):
        mock_task = Mock()
        mock_task.kill.side_effect = RuntimeError
        mock_pop_task.return_value = mock_task
        mock_pipe = Mock()
        self.worker_obj._kill_task({co.RESULT_PIPE: mock_pipe, co.CORRELATION_ID: "1"})
        mock_pipe.send.assert_called_once_with({co.RESULT: co.CODE_ERROR, co.OUTPUT: ""})

    @patch("cryton.worker.consumer.Consumer.pop_task")
    def test__kill_task_not_found(self, mock_pop_task):
        mock_pop_task.return_value = None
        mock_pipe = Mock()
        self.worker_obj._kill_task({co.RESULT_PIPE: mock_pipe, co.CORRELATION_ID: "1"})
        mock_pipe.send.assert_called_once_with({co.RESULT: co.CODE_ERROR, co.OUTPUT: "Couldn't find the Task."})

    @patch("cryton.worker.consumer.Consumer.pop_task")
    def test__finish_task(self, mock_pop_task):
        mock_task = Mock()
        mock_pop_task.return_value = mock_task

        self.worker_obj._finish_task({co.CORRELATION_ID: "1", co.DATA: ""})

        mock_pop_task.assert_called_once()

    @patch("cryton.worker.consumer.Consumer.send_message")
    def test__send_message(self, mock_send_message):
        self.worker_obj._send_message({co.QUEUE_NAME: "", co.DATA: "", co.PROPERTIES: {}})
        mock_send_message.assert_called_once()

    @patch("cryton.worker.triggers.HTTPListener.add_trigger")
    def test__add_trigger_new(self, mock_add_trigger):
        mock_pipe = Mock()
        test_id = "test_id"
        mock_add_trigger.return_value = test_id
        self.worker_obj._add_trigger({co.RESULT_PIPE: mock_pipe,
                                      co.DATA: {co.LISTENER_HOST: "", co.LISTENER_PORT: "",
                                                co.TRIGGER_TYPE: "HTTP"}})
        mock_pipe.send.assert_called_once_with({co.RESULT: co.CODE_OK, co.TRIGGER_ID: test_id})

    def test__add_trigger_existing(self):
        mock_trigger_obj = Mock()
        test_id = "test_id"
        mock_trigger_obj.compare_identifiers.return_value = True
        mock_trigger_obj.add_trigger.return_value = test_id
        mock_pipe = Mock()
        self.worker_obj._listeners.append(mock_trigger_obj)
        self.worker_obj._add_trigger(
            {co.RESULT_PIPE: mock_pipe,
             co.DATA: {co.LISTENER_HOST: "", co.LISTENER_PORT: "", co.TRIGGER_TYPE: "HTTP"}})
        mock_pipe.send.assert_called_once_with({co.RESULT: co.CODE_OK, co.TRIGGER_ID: test_id})

    def test__start_trigger_existing_error_adding_trigger(self):
        mock_trigger_obj = Mock()
        mock_trigger_obj.compare_identifiers.return_value = True
        mock_trigger_obj.add_trigger.side_effect = exceptions.TooManyTriggers("MSF")
        mock_pipe = Mock()
        self.worker_obj._listeners.append(mock_trigger_obj)
        self.worker_obj._add_trigger(
            {co.RESULT_PIPE: mock_pipe, co.DATA: {co.LISTENER_HOST: "", co.LISTENER_PORT: "", co.TRIGGER_TYPE: "MSF"}})
        mock_pipe.send.assert_called_once_with({co.RESULT: co.CODE_ERROR,
                                                co.OUTPUT: "Listener 'MSF' can't contain more triggers."})

    def test__add_trigger_pymetasploit_error(self):
        mock_trigger_obj = Mock()
        mock_trigger_obj.add_trigger.side_effect = ValueError("wrong option LHOST")
        mock_pipe = Mock()
        self.worker_obj._listeners.append(mock_trigger_obj)
        self.worker_obj._add_trigger(
            {co.RESULT_PIPE: mock_pipe, co.DATA: {co.LISTENER_HOST: "", co.LISTENER_PORT: "", co.TRIGGER_TYPE: "MSF"}})
        mock_pipe.send.assert_called_once_with({co.RESULT: co.CODE_ERROR,
                                                co.OUTPUT: "wrong option LHOST"})

    @patch("cryton.worker.worker.Listener", Mock())
    def test__remove_trigger_exists(self):
        mock_trigger_obj = Mock()
        mock_trigger_obj.compare_identifiers.return_value = True
        mock_trigger_obj.any_trigger_exists.return_value = False
        mock_trigger_obj.remove_trigger.return_value = None
        mock_pipe = Mock()
        self.worker_obj._listeners.append(mock_trigger_obj)
        self.worker_obj._remove_trigger({co.RESULT_PIPE: mock_pipe,
                                         co.DATA: {co.LISTENER_HOST: "", co.LISTENER_PORT: "",
                                                   co.TRIGGER_TYPE: "HTTP"}})
        mock_pipe.send.assert_called_once_with({co.RESULT: co.CODE_OK})

    def test__remove_trigger_not_found(self):
        mock_pipe = Mock()
        self.worker_obj._remove_trigger({co.RESULT_PIPE: mock_pipe,
                                         co.DATA: {co.LISTENER_HOST: "", co.LISTENER_PORT: "",
                                                   co.TRIGGER_TYPE: "HTTP"}})
        mock_pipe.send.assert_called_once_with(
            {co.RESULT: co.CODE_ERROR, co.OUTPUT: "Existing trigger not found."})

    def test__list_triggers(self):
        test_trigger = {"id": "test_id"}
        mock_trigger_obj = Mock()
        mock_trigger_obj.get_triggers.return_value = [test_trigger]
        mock_pipe = Mock()
        self.worker_obj._listeners.append(mock_trigger_obj)
        self.worker_obj._list_triggers({co.RESULT_PIPE: mock_pipe})
        mock_pipe.send.assert_called_once_with({co.RESULT: co.CODE_OK, co.TRIGGER_LIST: [test_trigger]})

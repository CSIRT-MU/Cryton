# import pytest
# from pytest_mock import MockerFixture
# from unittest.mock import patch, Mock, call
#
# import amqpstorm
# from queue import Empty
#
# from cryton.hive.services import listener
# from cryton.hive.utility import logger, states, constants
# from cryton.hive.cryton_app.models import CorrelationEventModel
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger(constants.LOGGER_CRYTON_TESTING))
# class TestChannelConsumer:
#     path = "cryton.hive.services.listener"
#
#     @pytest.fixture
#     def f_channel_consumer(self):
#         channel_consumer = listener.ChannelConsumer(1, Mock(), {"queue": "callback"})
#
#         return channel_consumer
#
#     def test___init__(self):
#         mock_channel = Mock()
#         mock_connection = Mock()
#         mock_connection.channel.return_value = mock_channel
#
#         result = listener.ChannelConsumer(1, mock_connection, {"queue": "callback"})
#
#         mock_connection.channel.assert_called_once()
#         mock_channel.basic.qos.assert_called_once_with(1)
#         mock_channel.queue.declare.assert_called_once_with("queue")
#         mock_channel.basic.consume.assert_called_once_with("callback", "queue")
#         assert result._id == 1
#         assert result._channel == mock_channel
#
#     def test__channel_consumer_connection_error(self, f_channel_consumer, caplog):
#         mock_channel = Mock()
#         mock_channel.is_closed = False
#         mock_channel.start_consuming.side_effect = amqpstorm.AMQPConnectionError
#         f_channel_consumer._channel = mock_channel
#
#         f_channel_consumer.start()
#
#         mock_channel.start_consuming.assert_called_once()
#         assert "Channel consumer encountered a connection error." in caplog.text
#         assert len(caplog.records) == 3
#
#     def test__channel_consumer_unknown_error(self, f_channel_consumer, caplog):
#         mock_channel = Mock()
#
#         def close_channel():
#             mock_channel.is_closed = True
#             raise ValueError
#
#         mock_channel.is_closed = False
#         mock_channel.start_consuming.side_effect = close_channel
#         f_channel_consumer._channel = mock_channel
#
#         f_channel_consumer.start()
#
#         mock_channel.start_consuming.assert_called_once()
#         assert "Channel consumer encountered an error." in caplog.text
#         assert len(caplog.records) == 3
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger(constants.LOGGER_CRYTON_TESTING))
# class TestConsumer:
#     path = "cryton.hive.services.listener"
#
#     @pytest.fixture
#     def f_amqpstorm_connection(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".amqpstorm.Connection")
#
#     @pytest.fixture
#     def f_process(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".Process")
#
#     def test_start(self, f_process):
#         consumer_obj = listener.Consumer(1, Mock(), {}, 1)
#
#         mock_process = Mock()
#
#         f_process.return_value = mock_process
#
#         consumer_obj.start()
#
#         mock_process.start.assert_called_once()
#
#     def test_check_if_finished(self):
#         consumer_obj = listener.Consumer(1, Mock(), {}, 1)
#
#         mock_process = Mock()
#         consumer_obj._process = mock_process
#
#         consumer_obj.check_if_finished()
#
#         mock_process.join.assert_called_once()
#
#     def test___call__(self):
#         mock__update_connection = Mock(return_value=True)
#         mock__start_channel_consumers = Mock()
#         mock_stop = Mock()
#         mock_queue = Mock()
#         mock_queue.get.return_value = None
#         mock_stopped = Mock()
#         mock_stopped.is_set.side_effect = [False, True]
#
#         consumer_obj = listener.Consumer(1, mock_queue, {}, 1)
#
#         consumer_obj._update_connection = mock__update_connection
#         consumer_obj._stopped = mock_stopped
#         consumer_obj._start_channel_consumers = mock__start_channel_consumers
#         consumer_obj.stop = mock_stop
#
#         consumer_obj()
#
#         mock__update_connection.assert_called_once()
#         mock__start_channel_consumers.assert_called_once()
#         mock_stop.assert_called_once()
#
#     def test___call___connection_error(self):
#         mock__update_connection = Mock(side_effect=amqpstorm.AMQPConnectionError)
#         mock_stopped = Mock()
#         mock_stopped.is_set.side_effect = [False, True]
#
#         consumer_obj = listener.Consumer(1, Mock(), {}, 1)
#
#         consumer_obj._update_connection = mock__update_connection
#         consumer_obj._stopped = mock_stopped
#
#         consumer_obj()
#
#         mock__update_connection.assert_called_once()
#
#     @pytest.mark.parametrize(
#         "p_queue_error",
#         [
#             Empty,
#             KeyboardInterrupt
#         ]
#     )
#     def test___call___empty_error(self, p_queue_error):
#         mock__update_connection = Mock(return_value=True)
#         mock__start_channel_consumers = Mock()
#         mock_queue = Mock()
#         mock_queue.get.side_effect = p_queue_error
#         mock_stopped = Mock()
#         mock_stopped.is_set.side_effect = [False, True]
#
#         consumer_obj = listener.Consumer(1, mock_queue, {}, 1)
#
#         consumer_obj._update_connection = mock__update_connection
#         consumer_obj._stopped = mock_stopped
#         consumer_obj._start_channel_consumers = mock__start_channel_consumers
#
#         consumer_obj()
#
#         mock__update_connection.assert_called_once()
#         mock__start_channel_consumers.assert_called_once()
#         mock_queue.get.assert_called_once()
#
#     def test_stop(self):
#         consumer_obj = listener.Consumer(1, Mock(), {}, 1)
#
#         mock_stopped = Mock()
#         mock_stopped.is_set.return_value = False
#         mock_channel = Mock()
#         mock_connection = Mock()
#         mock_connection.channels.values.return_value = [mock_channel]
#
#         consumer_obj._stopped = mock_stopped
#         consumer_obj._connection = mock_connection
#
#         consumer_obj.stop()
#
#         mock_connection.close.assert_called_once()
#         mock_channel.close.assert_called_once()
#
#     def test__update_connection_no_errors(self, f_amqpstorm_connection):
#         consumer_obj = listener.Consumer(1, Mock(), {}, 1)
#
#         mock_connection = Mock()
#         mock_connection.is_open = True
#         consumer_obj._connection = mock_connection
#
#         result = consumer_obj._update_connection()
#
#         assert result is False
#         f_amqpstorm_connection.assert_not_called()
#         assert consumer_obj._connection is not None
#
#     def test__update_connection_non_existent(self, f_amqpstorm_connection):
#         consumer_obj = listener.Consumer(1, Mock(), {}, 1)
#
#         result = consumer_obj._update_connection()
#
#         assert result is True
#         f_amqpstorm_connection.assert_called_once()
#         assert consumer_obj._connection is not None
#
#     def test__update_connection_closed(self, f_amqpstorm_connection):
#         consumer_obj = listener.Consumer(1, Mock(), {}, 1)
#
#         mock_connection = Mock()
#         mock_connection.is_open = False
#         consumer_obj._connection = mock_connection
#
#         result = consumer_obj._update_connection()
#
#         assert result is True
#         f_amqpstorm_connection.assert_called_once()
#
#     def test__update_connection_with_errors(self, f_amqpstorm_connection):
#         consumer_obj = listener.Consumer(1, Mock(), {}, 1)
#
#         mock_connection = Mock()
#         mock_connection.check_for_errors.side_effect = amqpstorm.AMQPError
#         consumer_obj._connection = mock_connection
#
#         result = consumer_obj._update_connection()
#
#         assert result is True
#         f_amqpstorm_connection.assert_called_once()
#
#     def test__update_connection_connection_error(self, f_amqpstorm_connection, caplog):
#         consumer_obj = listener.Consumer(1, Mock(), {}, 1)
#
#         f_amqpstorm_connection.side_effect = amqpstorm.AMQPConnectionError
#
#         with pytest.raises(amqpstorm.AMQPConnectionError):
#             consumer_obj._update_connection()
#
#         f_amqpstorm_connection.assert_called_once()
#         assert "Connection to RabbitMQ server established" not in caplog.text
#         assert len(caplog.records) == 1
#
#     def test__start_channel_consumers(self, mocker: MockerFixture):
#         consumer_obj = listener.Consumer(1, Mock(), {}, 1)
#
#         mock_channel_consumer = mocker.patch(self.path + ".ChannelConsumer")
#         mock_thread = mocker.patch(self.path + ".Thread")
#
#         consumer_obj._start_channel_consumers()
#
#         mock_channel_consumer.assert_called_once()
#         mock_thread.assert_called_once()
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger(constants.LOGGER_CRYTON_TESTING))
# class TestListener:
#     path = "cryton.hive.services.listener"
#
#     @pytest.fixture(autouse=True)
#     def f_scheduler_service(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".SchedulerService")
#
#     @pytest.fixture
#     def f_step_execution(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".step.StepExecution")
#
#     @pytest.fixture
#     def f_stage_execution(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".stage.StageExecution")
#
#     @pytest.fixture
#     def f_json_loads(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".json.loads")
#
#     @pytest.fixture
#     def f_plan_execution(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".plan.PlanExecution")
#
#     @pytest.fixture
#     def f_event(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".event.Event")
#
#     @pytest.fixture
#     def f_time_sleep(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".time.sleep")
#
#     @pytest.fixture
#     def f_correlation_event_model(self, mocker: MockerFixture):
#         return mocker.patch(self.path + ".CorrelationEventModel")
#
#     def test_start_blocking(self, f_time_sleep):
#         listener_obj = listener.Listener()
#
#         mock_stopped = Mock()
#         mock_stopped.is_set.side_effect = [False, True]
#         mock__start_consumers = Mock()
#
#         listener_obj._stopped = mock_stopped
#         listener_obj._start_consumers = mock__start_consumers
#
#         listener_obj.start()
#
#         mock__start_consumers.assert_called_once()
#         mock_stopped.is_set.assert_has_calls([call(), call()])
#
#     def test_start_non_blocking(self, f_time_sleep):
#         listener_obj = listener.Listener()
#
#         mock_stopped = Mock()
#         mock__start_consumers = Mock()
#
#         listener_obj._stopped = mock_stopped
#         listener_obj._start_consumers = mock__start_consumers
#
#         listener_obj.start(False)
#
#         mock__start_consumers.assert_called_once()
#         mock_stopped.is_set.assert_not_called()
#         f_time_sleep.assert_not_called()
#
#     def test_start_keyboard_interrupt(self, f_time_sleep):
#         listener_obj = listener.Listener()
#
#         mock_stopped = Mock()
#         mock_stopped.is_set.return_value = False
#         mock__start_consumers = Mock()
#         mock_stop = Mock()
#
#         listener_obj._stopped = mock_stopped
#         listener_obj._start_consumers = mock__start_consumers
#         listener_obj.stop = mock_stop
#
#         f_time_sleep.side_effect = KeyboardInterrupt
#
#         listener_obj.start()
#
#         mock__start_consumers.assert_called_once()
#         mock_stopped.is_set.assert_called_once()
#         mock_stop.assert_called_once()
#
#     def test_stop(self, f_scheduler_service):
#         listener_obj = listener.Listener()
#
#         mock_stopped = Mock()
#         mock_consumer = Mock()
#         mock_queue = Mock()
#
#         listener_obj._stopped = mock_stopped
#         listener_obj._consumers = [mock_consumer]
#         listener_obj._queue = mock_queue
#
#         listener_obj.stop()
#
#         mock_queue.put.assert_has_calls([call(None), call(None)])
#         mock_consumer.check_if_finished.assert_called_once_with()
#         f_scheduler_service.return_value.stop.assert_called_once()
#         mock_stopped.set.assert_called_once()
#
#     def test__start_consumers(self, mocker: MockerFixture):
#         listener_obj = listener.Listener()
#         listener_obj.consumers_count = 1
#
#         mock_consumer = mocker.patch(self.path + ".Consumer")
#
#         listener_obj._start_consumers()
#
#         mock_consumer.assert_called_once()
#         mock_consumer.return_value.start.assert_called_once()
#         assert listener_obj._consumers != {}
#
#     def test_step_response_callback(self, f_step_execution, f_json_loads, f_plan_execution, f_event):
#         listener_obj = listener.Listener()
#
#         mock_message = Mock()
#         mock_get_correlation_event = Mock()
#
#         listener_obj._get_correlation_event = mock_get_correlation_event
#
#         f_plan_execution.return_value.state = states.PENDING
#         f_step_execution.return_value.state = states.FINISHED
#
#         listener_obj.step_response_callback(mock_message)
#
#         mock_message.ack.assert_called_once()
#         mock_get_correlation_event.assert_called_once()
#         f_step_execution.assert_called_once()
#         mock_get_correlation_event.return_value.delete.assert_called_once()
#         f_json_loads.assert_called_once()
#         f_step_execution.return_value.postprocess.assert_called_once()
#         f_step_execution.return_value.ignore_successors.assert_called_once()
#         f_event.return_value.handle_finished_step.assert_called_once()
#         f_step_execution.return_value.execute_successors.assert_called_once()
#
#     def test_step_response_callback_error_state(self, f_step_execution, f_json_loads, f_plan_execution, f_event):
#         listener_obj = listener.Listener()
#
#         mock_message = Mock()
#         mock_get_correlation_event = Mock()
#
#         listener_obj._get_correlation_event = mock_get_correlation_event
#
#         f_plan_execution.return_value.state = states.PENDING
#         f_step_execution.return_value.state = states.ERROR
#
#         listener_obj.step_response_callback(mock_message)
#
#         mock_message.ack.assert_called_once()
#         mock_get_correlation_event.assert_called_once()
#         f_step_execution.assert_called_once()
#         mock_get_correlation_event.return_value.delete.assert_called_once()
#         f_json_loads.assert_called_once()
#         f_step_execution.return_value.postprocess.assert_called_once()
#         f_step_execution.return_value.ignore_successors.assert_called_once()
#         f_event.return_value.handle_finished_step.assert_called_once()
#
#     def test_step_response_callback_unknown_correlation_id(self, caplog):
#         listener_obj = listener.Listener()
#
#         mock_message = Mock()
#         mock_get_correlation_event = Mock()
#         mock_get_correlation_event.side_effect = CorrelationEventModel.DoesNotExist
#
#         listener_obj._get_correlation_event = mock_get_correlation_event
#
#         listener_obj.step_response_callback(mock_message)
#
#         mock_message.ack.assert_called_once()
#         mock_get_correlation_event.assert_called_once()
#         assert "Received nonexistent correlation_id" in caplog.text
#
#     def test_step_response_callback_pausing(self, f_step_execution, f_json_loads, f_plan_execution, f_event):
#         listener_obj = listener.Listener()
#
#         mock_message = Mock()
#         mock_get_correlation_event = Mock()
#         mock_handle_pausing = Mock()
#
#         listener_obj._get_correlation_event = mock_get_correlation_event
#         listener_obj._handle_pausing = mock_handle_pausing
#
#         f_plan_execution.return_value.state = states.PAUSING
#
#         listener_obj.step_response_callback(mock_message)
#
#         mock_message.ack.assert_called_once()
#         mock_get_correlation_event.assert_called_once()
#         f_step_execution.assert_called_once()
#         mock_get_correlation_event.return_value.delete.assert_called_once()
#         f_json_loads.assert_called_once()
#         f_step_execution.return_value.postprocess.assert_called_once()
#         f_step_execution.return_value.ignore_successors.assert_called_once()
#         f_event.return_value.handle_finished_step.assert_called_once()
#         f_step_execution.return_value.execute_successors.assert_not_called()
#
#     def test_event_callback_trigger_stage(self, f_event, f_json_loads):
#         listener_obj = listener.Listener()
#
#         mock_message = Mock()
#
#         f_json_loads.return_value = {constants.EVENT_T: constants.EVENT_TRIGGER_STAGE, constants.EVENT_V: {}}
#
#         listener_obj.event_callback(mock_message)
#
#         mock_message.ack.assert_called_once()
#         f_event.return_value.trigger_stage.assert_called_once()
#
#     def test_event_callback_handle_finished_step(self, f_event, f_json_loads):
#         listener_obj = listener.Listener()
#
#         mock_message = Mock()
#
#         f_json_loads.return_value = {constants.EVENT_T: constants.EVENT_STEP_EXECUTION_ERROR, constants.EVENT_V: {}}
#
#         listener_obj.event_callback(mock_message)
#
#         mock_message.ack.assert_called_once()
#         f_event.return_value.handle_finished_step.assert_called_once()
#
#     def test_event_callback_unknown_event_t(self, f_json_loads, caplog):
#         listener_obj = listener.Listener()
#
#         mock_message = Mock()
#
#         f_json_loads.return_value = {constants.EVENT_T: "UNKNOWN", constants.EVENT_V: {}}
#
#         listener_obj.event_callback(mock_message)
#
#         mock_message.ack.assert_called_once()
#         assert "Nonexistent event received" in caplog.text
#
#     def test_event_callback_message_parsing_error(self, f_json_loads, caplog):
#         listener_obj = listener.Listener()
#
#         mock_message = Mock()
#
#         f_json_loads.return_value = {}
#
#         listener_obj.event_callback(mock_message)
#
#         mock_message.ack.assert_called_once()
#         assert "Event must contain event_t and event_v!" in caplog.text
#
#     def test_control_request_callback(self, f_event, f_json_loads):
#         listener_obj = listener.Listener()
#
#         mock_message = Mock()
#         mock__send_response = Mock()
#         mock_scheduler_job_queue = Mock()
#
#         listener_obj._send_response = mock__send_response
#         listener_obj._scheduler_job_queue = mock_scheduler_job_queue
#
#         f_json_loads.return_value = {constants.EVENT_T: constants.EVENT_UPDATE_SCHEDULER, constants.EVENT_V: {}}
#         f_event.return_value.update_scheduler.return_value = 0
#
#         listener_obj.control_request_callback(mock_message)
#
#         mock_message.ack.assert_called_once()
#         listener_obj._scheduler_job_queue.put.assert_called_once()
#         mock__send_response.assert_called_once_with(mock_message, {constants.RETURN_VALUE: 0})
#
#     def test_control_request_callback_unknown_event_t(self, f_json_loads, caplog):
#         listener_obj = listener.Listener()
#
#         mock_message = Mock()
#         mock__send_response = Mock()
#
#         listener_obj._send_response = mock__send_response
#
#         f_json_loads.return_value = {constants.EVENT_T: "UNKNOWN", constants.EVENT_V: {}}
#
#         listener_obj.control_request_callback(mock_message)
#
#         mock_message.ack.assert_called_once()
#         assert "Nonexistent event received" in caplog.text
#         mock__send_response.assert_called_once_with(mock_message, {constants.RETURN_VALUE: -1})
#
#     def test_control_request_callback_message_parsing_error(self, f_json_loads, caplog):
#         listener_obj = listener.Listener()
#
#         mock_message = Mock()
#         mock__send_response = Mock()
#
#         listener_obj._send_response = mock__send_response
#
#         f_json_loads.return_value = {}
#
#         listener_obj.control_request_callback(mock_message)
#
#         mock_message.ack.assert_called_once()
#         assert "Control request must contain event_t and event_v!" in caplog.text
#         mock__send_response.assert_called_once_with(mock_message, {constants.RETURN_VALUE: -1})
#
#     def test__get_correlation_event(self, f_correlation_event_model):
#         listener_obj = listener.Listener()
#
#         mock_correlation_event_obj = Mock()
#
#         f_correlation_event_model.objects.get.return_value = mock_correlation_event_obj
#
#         result = listener_obj._get_correlation_event("id")
#
#         assert result == mock_correlation_event_obj
#
#     def test__get_correlation_event_timeout(self, mocker: MockerFixture, f_time_sleep, f_correlation_event_model):
#         listener_obj = listener.Listener()
#
#         mock_time_time = mocker.patch(self.path + ".time.time")
#         mock_time_time.side_effect = [0, 0, 99999]
#
#         f_correlation_event_model.DoesNotExist = CorrelationEventModel.DoesNotExist
#         f_correlation_event_model.objects.get.side_effect = CorrelationEventModel.DoesNotExist
#
#         with pytest.raises(CorrelationEventModel.DoesNotExist):
#             listener_obj._get_correlation_event("id")
#
#     def test__handle_pausing_pause_all(self, f_stage_execution, f_plan_execution, mocker: MockerFixture, caplog):
#         listener_obj = listener.Listener()
#
#         mock_step_ex_obj = Mock()
#
#         mock_timezone_now = mocker.patch(self.path + ".timezone.now")
#
#         mock_run = mocker.patch(self.path + ".run.Run")
#         mock_run.return_value.state = states.PAUSING
#         mock_run.return_value.model.plan_executions.all.return_value.exclude.return_value.exists \
#             .return_value = False
#
#         f_stage_execution.return_value.state = states.PAUSING
#         f_stage_execution.return_value.model.step_executions.all.return_value.exclude.return_value.exists\
#             .return_value = False
#
#         f_plan_execution.return_value.state = states.PAUSING
#         f_plan_execution.return_value.model.stage_executions.all.return_value.exclude.return_value.exists \
#             .return_value = False
#
#         listener_obj._handle_pausing(mock_step_ex_obj)
#
#         mock_step_ex_obj.pause_successors.assert_called_once()
#         mock_timezone_now.assert_has_calls([call(), call(), call()])
#         assert "Stage execution paused" in caplog.text
#         assert "Plan execution paused" in caplog.text
#         assert "Run paused" in caplog.text
#
#     @pytest.mark.parametrize("stage_state", states.PLAN_STAGE_PAUSE_STATES)
#     def test__handle_pausing_valid_pause_stage_states(self, f_stage_execution, f_plan_execution, mocker: MockerFixture,
#                                                       caplog, stage_state):
#         listener_obj = listener.Listener()
#
#         mock_step_ex_obj = Mock()
#
#         mocker.patch(self.path + ".run.Run")
#
#         f_stage_execution.return_value.state = stage_state
#
#         listener_obj._handle_pausing(mock_step_ex_obj)
#
#         mock_step_ex_obj.pause_successors.assert_not_called()
#         assert "Stage execution paused" not in caplog.text
#         assert "Plan execution paused" not in caplog.text
#         assert "Run paused" not in caplog.text
#
#     def test__handle_pausing_unfinished_steps(self, f_stage_execution, f_plan_execution, mocker: MockerFixture, caplog):
#         listener_obj = listener.Listener()
#
#         mock_step_ex_obj = Mock()
#
#         mocker.patch(self.path + ".run.Run")
#         mock_timezone_now = mocker.patch(self.path + ".timezone.now")
#
#         f_stage_execution.return_value.state = states.PAUSING
#         f_stage_execution.return_value.model.step_executions.all.return_value.exclude.return_value.exists \
#             .return_value = True
#
#         listener_obj._handle_pausing(mock_step_ex_obj)
#
#         mock_step_ex_obj.pause_successors.assert_called_once()
#         mock_timezone_now.assert_not_called()
#         assert "Stage execution paused" not in caplog.text
#         assert "Plan execution paused" not in caplog.text
#         assert "Run paused" not in caplog.text
#
#     def test__send_response(self, mocker: MockerFixture):
#         listener_obj = listener.Listener()
#
#         mock_message = Mock()
#         mock_message.reply_to = "queue"
#         mock_message.correlation_id = "id"
#         mock_client = mocker.patch(self.path + ".rabbit_client.Client")
#
#         listener_obj._send_response(mock_message, {})
#
#         mock_client.return_value.__enter__.return_value.send_message\
#             .assert_called_once_with("queue", {}, {'correlation_id': 'id'})

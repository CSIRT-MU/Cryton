# from unittest import TestCase
# from unittest.mock import patch, Mock
#
# from cryton.worker.triggers import HTTPListener, Listener, ListenerEnum, exceptions, MSFListener
# from cryton.worker.triggers.listener_http import MyWSGIRefServer
# from cryton.worker.util import constants as co
#
#
# class TestMyWSGIRefServer(TestCase):
#
#     @patch("cryton.worker.triggers.listener_http.make_server")
#     def test_run(self, mock_make_server):
#         mock_server = Mock()
#         mock_make_server.return_value = mock_server
#         server = MyWSGIRefServer()
#
#         server.run(Mock())
#
#         mock_server.serve_forever.assert_called_once()
#
#     def test_stop(self):
#         mock_server = Mock()
#         server = MyWSGIRefServer()
#         server.server = mock_server
#
#         server.stop()
#
#         mock_server.shutdown.assert_called_once()
#         mock_server.server_close.assert_called_once()
#
# class TestListenerEnum(TestCase):
#     def test_get_correct_item(self):
#         result = ListenerEnum["HTTP"]
#         self.assertEqual(result, HTTPListener)
#
#     def test_get_wrong_item(self):
#         with self.assertRaises(exceptions.ListenerTypeDoesNotExist):
#             _ = ListenerEnum["WRONG"]
#
#
# class TestListener(TestCase):
#     def setUp(self):
#         self.mock_main_queue = Mock()
#         self.listener_obj = Listener(self.mock_main_queue)
#
#     def test_start(self):
#         self.listener_obj.start()
#
#     def test_stop(self):
#         self.listener_obj.stop()
#
#     def test_add_trigger(self):
#         self.listener_obj.add_trigger({})
#
#     def test_remove_trigger(self):
#         self.listener_obj.remove_trigger({})
#
#     def test_find_trigger(self):
#         self.assertIsNone(self.listener_obj.find_trigger(""))  # No trigger is found
#
#         test_trigger = {co.TRIGGER_ID: "test_id"}
#         self.listener_obj._triggers.append(test_trigger)
#         result = self.listener_obj.find_trigger("test_id")
#         self.assertEqual(result, test_trigger)
#
#     def test_get_triggers(self):
#         test_trigger = {co.TRIGGER_ID: "test_id"}
#         self.listener_obj._triggers.append(test_trigger)
#         result = self.listener_obj.get_triggers()
#         self.assertEqual(result, [test_trigger])
#
#     def test_any_trigger_exists_true(self):
#         self.listener_obj._triggers.append({})
#         result = self.listener_obj.any_trigger_exists()
#         self.assertTrue(result)
#
#     def test_any_trigger_exists_false(self):
#         result = self.listener_obj.any_trigger_exists()
#         self.assertFalse(result)
#
#     def test__notify(self):
#         q_name = "queue_name"
#         msg_body = {}
#         self.listener_obj._notify(q_name, msg_body)
#         self.mock_main_queue.put.assert_called_once()
#
#
# class TestHTTPListener(TestCase):
#     @patch("bottle.Bottle", Mock())
#     def setUp(self):
#         self.mock_main_queue = Mock()
#         self.details = {"type": "HTTP", "host": "test", "port": 8082, "event_q": "test", "stage_ex_id": 1, "routes": [
#             {"path": "test", "method": "GET", "parameters": [{"name": "a", "value": "1"}]}]}
#         self.listener_obj = HTTPListener(self.mock_main_queue, host="test", port=8082)
#
#     @patch("cryton.worker.triggers.listener_http.HTTPListener._restart")
#     def test_add_trigger(self, mock_restart):
#         self.listener_obj.add_trigger(self.details)
#         mock_restart.assert_called()
#
#     @patch("cryton.worker.triggers.listener_http.HTTPListener._restart")
#     def test_remove_trigger(self, mock_restart):
#         self.listener_obj._triggers.append(self.details)
#         self.listener_obj.remove_trigger(self.details)
#         mock_restart.assert_called()
#
#     @patch("cryton.worker.triggers.listener_http.HTTPListener.stop")
#     def test__restart_only_stop(self, mock_stop):
#         self.listener_obj._stopped = False
#         self.listener_obj._restart()
#         mock_stop.assert_called()
#
#     @patch("cryton.worker.triggers.listener_http.HTTPListener.start")
#     @patch("cryton.worker.triggers.listener_http.HTTPListener.stop")
#     def test__restart(self, mock_stop, mock_start):
#         self.listener_obj._stopped = False
#         self.listener_obj._triggers.append(self.details)
#         self.listener_obj._restart()
#         mock_stop.assert_called()
#         mock_start.assert_called()
#
#     def test_compare_identifiers_match(self):
#         result = self.listener_obj.compare_identifiers(self.details)
#         self.assertTrue(result)
#
#     def test_get_triggers_num(self):
#         self.listener_obj._triggers.append(self.details)
#         ret = self.listener_obj.any_trigger_exists()
#         self.assertEqual(ret, 1)
#
#     @patch("cryton.worker.triggers.listener_http.HTTPListener._check_parameters")
#     @patch("cryton.worker.triggers.listener_http.HTTPListener._notify")
#     @patch("bottle.request")
#     def test__handle_request(self, mock_req, mock_send, mock_params):
#         mock_req.method = "GET"
#         mock_req.path = "test"
#         mock_params.return_value = True
#         self.listener_obj._triggers.append(self.details)
#         self.listener_obj._handle_request()
#         mock_send.assert_called()
#
#     @patch("bottle.request")
#     def test__check_parameters_get_ok(self, mock_req):
#         mock_req.method = "GET"
#         mock_req.query = {"tire": 15, "hammer": 25}
#         parameters = [{"name": "tire", "value": 15}, {"name": "hammer", "value": 25}]
#         ret = self.listener_obj._check_parameters(parameters)
#         self.assertTrue(ret)
#
#     @patch("bottle.request")
#     def test__check_parameters_get_fail(self, mock_req):
#         mock_req.method = "GET"
#         mock_req.query = {"tire": 99}
#         parameters = [{"name": "tire", "value": 15}]
#         ret = self.listener_obj._check_parameters(parameters)
#         self.assertFalse(ret)
#
#     @patch("bottle.request")
#     def test__check_parameters_post_ok(self, mock_req):
#         mock_req.method = "POST"
#         mock_req.forms = {"tire": 15, "hammer": 25}
#         parameters = [{"name": "tire", "value": 15}, {"name": "hammer", "value": 25}]
#         ret = self.listener_obj._check_parameters(parameters)
#         self.assertTrue(ret)
#
#     @patch("bottle.request")
#     def test__check_parameters_post_fail(self, mock_req):
#         mock_req.method = "POST"
#         mock_req.forms = {"tire": 99}
#         parameters = [{"name": "tire", "value": 15}]
#         ret = self.listener_obj._check_parameters(parameters)
#         self.assertFalse(ret)
#
#     @patch("bottle.request")
#     def test__check_parameters_fail(self, mock_req):
#         mock_req.method = "DELETE"
#         mock_req.forms = {"tire": 99}
#         parameters = [{"name": "tire", "value": 15}]
#         ret = self.listener_obj._check_parameters(parameters)
#         self.assertFalse(ret)
#
#     @patch("threading.Thread.start")
#     def test_start(self, mock_start):
#         self.listener_obj._stopped = True
#         self.listener_obj.start()
#         mock_start.assert_called()
#
#     def test_stop(self):
#         self.listener_obj._stopped = False
#         mock_server = Mock()
#         self.listener_obj.server = mock_server
#
#         self.listener_obj.stop()
#         mock_server.stop.assert_called()
#
#     @patch("cryton.worker.triggers.listener_http.MyWSGIRefServer")
#     def test__run(self, mock_wsgi_server):
#         mock_app = Mock()
#         mock_wsgi_server.return_value = Mock()
#         self.listener_obj._app = mock_app
#
#         self.listener_obj._run()
#
#         mock_app.run.assert_called_once()
#
#
# class TestMSFListener(TestCase):
#     @patch("cryton.worker.util.util.Metasploit")
#     def setUp(self, mock_msf):
#         self.mock_msf = mock_msf
#         self.mock_msf.is_connected.return_value = True
#         self.mock_main_queue = Mock()
#         self.details = {"type": "MSF", "reply_to": "", "exploit": "", "exploit_arguments": {},
#                         "payload": "", "payload_arguments": {}, "identifiers": {}}
#         self.listener_obj = MSFListener(self.mock_main_queue, identifiers={})
#
#     def test_compare_identifiers_match(self):
#         result = self.listener_obj.compare_identifiers(self.details)
#         self.assertTrue(result)
#
#     @patch("cryton.worker.triggers.listener_msf.MSFListener.start")
#     @patch("cryton.worker.triggers.listener_base.Listener._generate_id")
#     def test_add_trigger(self, mock_gen, mock_start):
#         mock_gen.return_value = "1"
#         result = self.listener_obj.add_trigger(self.details)
#         self.assertEqual(result, "1")
#         mock_start.assert_called_once()
#
#     @patch("cryton.worker.triggers.listener_msf.MSFListener.any_trigger_exists")
#     def test_add_trigger_error(self, mock_exists):
#         mock_exists.return_value = True
#         with self.assertRaises(exceptions.TooManyTriggers):
#             self.listener_obj.add_trigger(self.details)
#
#     @patch("cryton.worker.triggers.listener_msf.MSFListener.stop")
#     def test_remove_trigger(self, mock_stop):
#         self.listener_obj._triggers.append(self.details)
#         self.listener_obj.remove_trigger(self.details)
#         mock_stop.assert_called_once()
#
#     @patch("time.sleep", Mock())
#     @patch("cryton.worker.triggers.listener_msf.MSFListener._notify")
#     def test__check_for_session(self, mock_notify):
#         self.mock_msf.return_value.get_sessions.return_value = ["1"]
#         self.listener_obj._triggers.append(self.details)
#         self.listener_obj._stopped = False
#         self.listener_obj._check_for_session()
#         mock_notify.assert_called_once()
#
#     @patch("copy.deepcopy", Mock())
#     @patch("threading.Thread.start")
#     def test_start(self, mock_thread):
#         self.listener_obj._triggers.append(self.details)
#         self.listener_obj.start()
#         self.assertFalse(self.listener_obj._stopped)
#         mock_thread.assert_called_once()
#
#     @patch("copy.deepcopy", Mock())
#     def test_start_msf_exception(self):
#         self.mock_msf.return_value.is_connected.return_value = False
#         self.listener_obj._triggers.append(self.details)
#         with self.assertRaises(exceptions.MsfConnectionError):
#             self.listener_obj.start()
#
#     def test_stop(self):
#         self.listener_obj._stopped = False
#         self.listener_obj.stop()
#         self.assertTrue(self.listener_obj._stopped)

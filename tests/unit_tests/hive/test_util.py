from django.test import TestCase
from unittest.mock import patch, MagicMock, call, Mock, mock_open
import os
import datetime
import pytz
from model_bakery import baker


from cryton_core.lib.util import util

from cryton_core.cryton_app.models import WorkerModel

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


@patch('cryton_core.lib.util.util.logger.logger', util.logger.structlog.getLogger('cryton-core-debug'))
@patch('amqpstorm.Connection', Mock())
class TestUtil(TestCase):

    def setUp(self) -> None:
        self.worker = baker.make(WorkerModel)

    def test_convert_to_utc(self):
        original_datetime = datetime.datetime.now()
        ret = util.convert_to_utc(original_datetime)
        self.assertEqual(ret, original_datetime)

    def test_convert_to_utc_localized(self):
        original_datetime = pytz.timezone('utc').localize(datetime.datetime.now())
        ret = util.convert_to_utc(original_datetime, offset_aware=True)
        self.assertEqual(ret, original_datetime)

    def test_convert_from_utc(self):
        original_datetime = datetime.datetime.now()
        ret = util.convert_from_utc(original_datetime, 'utc')
        self.assertEqual(ret, original_datetime)

    def test_convert_from_utc_localized(self):
        original_datetime = pytz.timezone('utc').localize(datetime.datetime.now())
        ret = util.convert_from_utc(original_datetime, 'utc', True)
        self.assertEqual(ret, original_datetime)

    def test_split_into_lists(self):
        input_list = [1, 2, 3]
        ret = util.split_into_lists(input_list, 3)
        self.assertEqual(ret, [[1], [2], [3]])

        input_list = [1, 2, 3, 4]
        ret = util.split_into_lists(input_list, 3)
        self.assertEqual(ret, [[1, 2], [3], [4]])

        input_list = [1, 2]
        ret = util.split_into_lists(input_list, 3)
        self.assertEqual(ret, [[1], [2], []])

    # @patch("cryton_core.lib.util.util.amqpstorm.Connection")
    @patch("cryton_core.lib.util.util.run_step_executions")
    @patch("cryton_core.lib.util.util.split_into_lists", Mock(return_value=["exec1", "exec2", "exec3"]))
    @patch("cryton_core.lib.util.util.Thread")
    def test_run_executions_in_threads(self, mock_thread, mock_run_step_executions):
        mock_conn = MagicMock()
        mock_connection = MagicMock()
        mock_connection.return_value.__enter__.return_value = mock_conn
        patch_connection = patch("cryton_core.lib.util.util.amqpstorm.Connection", mock_connection)
        patch_connection.start()

        util.run_executions_in_threads(["exec1", "exec2", "exec3"])

        mock_thread.assert_has_calls([
            call(target=mock_run_step_executions, args=(mock_conn, "exec1")),
            call(target=mock_run_step_executions, args=(mock_conn, "exec2")),
            call(target=mock_run_step_executions, args=(mock_conn, "exec3"))]
        )

    def test_run_step_executions(self):
        step_exec1 = MagicMock()
        step_exec2 = MagicMock()
        connection = MagicMock()
        channel = MagicMock()

        connection.channel.return_value.__enter__.return_value = channel

        util.run_step_executions(connection, [step_exec1, step_exec2])

        step_exec1.execute.assert_called_with(channel)
        step_exec2.execute.assert_called_with(channel)

    def test_parse_dot_argument(self):
        test_arg = "[te[1]st[s][][1]"
        result = util.parse_dot_argument(test_arg)
        self.assertEqual(["[te[1]st[s][]", "[1]"], result)

    def test_parse_dot_argument_no_index(self):
        test_arg = "test"
        result = util.parse_dot_argument(test_arg)
        self.assertEqual([test_arg], result)

    @patch("cryton_core.lib.util.util.parse_dot_argument")
    def test_get_from_mod_in(self, mock_parse_dot_arg):
        mock_parse_dot_arg.side_effect = [["parent"], ["output"], ["username"]]
        resp = util.get_from_dict({'parent': {'output': {'username': 'admin'}}}, '$parent.output.username', ".")
        self.assertEqual(resp, 'admin')

        mock_parse_dot_arg.side_effect = [["a", "[1]"], ["c"]]
        resp = util.get_from_dict({'a': [{'b': 1}, {'c': 2}]}, '$a[1].c', '.')
        self.assertEqual(resp, 2)

    # TODO: rework with parametrize when we switch to pytest
    # TODO: also isn't this more of a functional test?
    def test_fill_dynamic_variables(self):
        separators = [".", "|"]
        for separator in separators:
            with self.subTest(separator):
                mod_in = {'parent': {'t1': {'t2': 666}}}

                args = {
                    'arg1': 1,
                    'arg2': {
                        'test': f'$parent{separator}t1{separator}t2'
                    },
                    'arg3': [1, 2, 3],
                    'arg4': [
                        {1: f'$parent{separator}test;'}
                    ],
                    'arg5': {
                        '1': {
                            '2': f'$parent{separator}test;'
                        }
                    }
                }

                util.fill_dynamic_variables(args, mod_in, separator)

                self.assertEqual(args.get('arg2').get('test'), 666)
                self.assertEqual(args.get('arg4')[0].get(1), f'$parent{separator}test;')
                self.assertEqual(args.get('arg5').get('1').get('2'), f'$parent{separator}test;')

    def test_rename_key(self):
        dict_in = {'1': 1, '2': 2, '3': {'4': {'5': 6}, '7': 8}}
        rename_from = '3.4'
        rename_to = '9.10.11'
        expected = {'1': 1, '2': 2, '3': {'7': 8}, '9': {'10': {'11': {'5': 6}}}}

        util.rename_key(dict_in, rename_from, rename_to)
        self.assertEqual(dict_in, expected)

        dict_in = {'1': 1, '2': 2}
        rename_from = '2'
        rename_to = '6'
        expected = {'1': 1, '6': 2}

        util.rename_key(dict_in, rename_from, rename_to)
        self.assertEqual(dict_in, expected)

        dict_in = {'1': 1, '2': 2}
        rename_from = '3'
        rename_to = '6'

        with self.assertRaises(KeyError):
            util.rename_key(dict_in, rename_from, rename_to)

    @patch("cryton_core.lib.util.util.open", mock_open(read_data='{"a": 1} \n{"a": 2} \n {"a": 3} \n'))
    def test_get_logs(self):
        result = util.get_logs(0, 0, [""])

        self.assertEqual([{'a': 1}, {'a': 2}, {'a': 3}], result)

    @patch("cryton_core.lib.util.util.open", mock_open(read_data='{"a": 1} \n{"a": 2} \n {"a": 3} \n'))
    def test_get_logs_filter(self):
        result = util.get_logs(0, 0, ["2"])

        self.assertEqual([{'a': 2}], result)

    @patch("cryton_core.lib.util.util.open", mock_open(read_data='{"a": 1} \n{"a": 2} \n {\'a\': 3} \n'))
    def test_get_logs_json_error(self):
        result = util.get_logs(0, 0, [""])

        self.assertEqual([{'a': 1}, {'a': 2}, {"detail": "{'a': 3}"}], result)

    # @pytest.mark.parametrize(
    #     "p_request_params, p_response_count, p_response_results",
    #     [
    #         ({}, 3, [{'a': 1}, {'a': 2}, {'b': 3}]),
    #         ({'offset': 1, 'limit': 0}, 3, [{'a': 2}, {'b': 3}]),
    #         ({'offset': 1, 'limit': 1}, 3, [{'a': 2}]),
    #         ({'filter': 'a'}, 2, [{'a': 1}, {'a': 2}]),
    #         ({'filter': 'a', 'limit': 1}, 2, [{'a': 1}]),
    #     ]
    # )

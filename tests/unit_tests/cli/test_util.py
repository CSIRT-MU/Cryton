from unittest.mock import Mock, mock_open
import pytest
import requests
import click
from datetime import datetime

from cryton_cli.lib.util import util


class TestUtil:
    path = "cryton_cli.lib.util.util"
    plan_dict = {"plan": "plan"}

    def test_save_yaml_to_file(self, mocker):
        mocker.patch('builtins.open', mock_open())
        mock_datetime = mocker.patch(self.path + '.datetime')
        mock_datetime.now.return_value.strftime.return_value = "timestamp"
        mock_random_choices = mocker.patch(self.path + '.random.choices')
        mock_random_choices.return_value = "tail"

        result = util.save_yaml_to_file(self.plan_dict, '/tmp', 'test')

        assert "/tmp/test_timestamp_tail" == result

    def test_save_yaml_to_file_error(self, mocker):
        mocker.patch('builtins.open', Mock(side_effect=IOError))
        mock_datetime = mocker.patch(self.path + '.datetime')
        mock_datetime.now.return_value.strftime.return_value = "timestamp"
        mock_random_choices = mocker.patch(self.path + '.random.choices')
        mock_random_choices.return_value = "tail"

        with pytest.raises(IOError):
            util.save_yaml_to_file(self.plan_dict, '/tmp', 'test')

    def test_convert_from_utc(self, mocker):
        test_datetime = datetime.utcnow()
        str_test_datetime = str(test_datetime).replace(' ', 'T') + "Z"

        mocker.patch(self.path + '.config.TIME_ZONE', 'utc')

        ret = util.convert_from_utc(str_test_datetime)

        assert test_datetime == ret

    def test_render_documentation(self):
        raw_docs = {
            'name': 'test', 'help': '  \n\n  test  \n\n  ', 'params': [
                {'param_type_name': 'argument', 'name': 'arg'},
                {'param_type_name': 'option', 'name': 'opt', 'opts': ['-l'], 'help': 'test'},
                {'param_type_name': 'option', 'name': 'opt2', 'opts': ['-l', '--ll'], 'help': 'test'},
            ],
            'commands':
                {'sub': {'name': 'sub', 'help': '   \n\n  sub  \n\n   ', 'params': [
                    {'param_type_name': 'argument', 'name': 'arg'},
                    {'param_type_name': 'option', 'name': 'opt', 'opts': ['-l'], 'help': 'test'},
                ]}}
        }
        result = util.render_documentation(raw_docs, 2)
        assert len(result) == 186

    def test_clean_up_documentation(self):
        result = util.clean_up_documentation('_')
        assert result == r'\_'

    def test_load_files(self, mocker):
        mocker.patch('builtins.open', mock_open(read_data=b'test'))

        result = util.load_files([""])

        assert result == {"0": b'test'}


class TestCliUtil:
    path = "cryton_cli.lib.util.util"
    request_url = 'http://test.test/test/'
    response_text = '{"detail": "response"}'
    response_json = {'detail': 'response'}

    @pytest.fixture
    def f_parse_response(self, mocker) -> Mock:
        return mocker.patch(self.path + '.parse_response')

    @pytest.fixture
    def f_save_yaml_to_file(self, mocker) -> Mock:
        return mocker.patch(self.path + '.save_yaml_to_file')

    @pytest.fixture
    def f_format_report(self, mocker) -> Mock:
        return mocker.patch(self.path + '.format_report')

    def test_cli_context(self, mocker):
        mocker.patch(self.path + '.config.API_SSL', True)
        mock_url = mocker.patch(self.path + '.api.create_rest_api_url')
        mock_url.return_value = 'test'
        ret = util.CliContext(None, None, False, False)

        assert mock_url.return_value == ret.api_url

    @pytest.mark.parametrize(
        "p_data, p_parsed_data",
        [
            ("text", 'Unable to parse response details.'),
            ('{"id": 1, "detail": ""}', {"id": 1, "detail": ""}),
            ('{"ids": [1], "detail": ""}', {"ids": [1], "detail": ""}),
            ('{"detail": "test"}', "test"),
            ('{"other": "test"}', {"other": "test"}),
            ('{"results": []}', []),
            ('["error", "other error"]', "error\n\n other error"),
            ('', "Empty response."),
        ]
    )
    def test_parse_response(self, p_data, p_parsed_data, requests_mock):
        requests_mock.get(self.request_url, text=p_data)
        response = requests.get(self.request_url)
        result = util.parse_response(response)
        assert result == p_parsed_data

    def test_echo_msg(self, requests_mock):
        requests_mock.get(self.request_url, text=self.response_text)
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.echo = Mock(return_value=1)

        assert util.echo_msg(response) is True
        click_echo.echo.assert_called_with('\x1b[32mSuccess!\x1b[0m (response)')

    def test_echo_msg_debug(self, requests_mock, f_parse_response):
        requests_mock.get(self.request_url, text=self.response_text)
        f_parse_response.return_value = self.response_json
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.echo = Mock(return_value=1)

        assert util.echo_msg(response, debug=True) is True
        click_echo.echo.assert_called_with(self.response_text)

    def test_echo_msg_fail(self, requests_mock):
        requests_mock.get(self.request_url, text=self.response_text, status_code=500)
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.echo = Mock(return_value=1)

        assert util.echo_msg(response) is False
        click_echo.echo.assert_called_with('\x1b[31mresponse\x1b[0m (None)')

    @staticmethod
    def test_echo_msg_connection_error():
        response = 'err'
        click_echo = click
        click_echo.secho = Mock(return_value=1)

        assert util.echo_msg(response) is False
        click_echo.secho.assert_called_with('err', fg='red')

    def test_echo_list(self, requests_mock, f_parse_response):
        requests_mock.get(self.request_url, text=self.response_text)
        f_parse_response.return_value = [{'id': 10, 'name': 'name', 'ignore': 'ignore me'}]
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.echo = Mock(return_value=1)

        util.echo_list(response, ['id', 'name'])
        click_echo.echo.assert_called_with('id: 10, name: name')

    def test_echo_list_empty(self, requests_mock, f_parse_response):
        requests_mock.get(self.request_url, text=self.response_text)
        f_parse_response.return_value = []
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.secho = Mock(return_value=1)

        util.echo_list(response, ['ignore'])
        click_echo.secho.assert_called_with('No matching objects...', fg='green')

    def test_echo_list_debug(self, requests_mock):
        requests_mock.get(self.request_url, text=self.response_text)
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.echo = Mock(return_value=1)

        util.echo_list(response, ['id', 'name'], debug=True)
        click_echo.echo.assert_called_with(self.response_text)

    def test_echo_list_localize(self, requests_mock, f_parse_response, mocker):
        mocker.patch(self.path + '.config.TIME_ZONE', 'utc')
        requests_mock.get(self.request_url, text=self.response_text)
        f_parse_response.return_value = [{'id': 10, 'name': 'name', 'ignore': 'ignore me',
                                          'pause_time': '2020-1-1T1:1:1.1Z'}]
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.echo = Mock(return_value=1)

        util.echo_list(response, ['id', 'name', 'pause_time'], localize=True)
        click_echo.echo.assert_called_with('id: 10, name: name, pause_time: 2020-01-01 01:01:01.100000')

    def test_echo_list_more(self, requests_mock, f_parse_response):
        requests_mock.get(self.request_url, text=self.response_text)
        f_parse_response.return_value = [{'id': 10, 'name': 'name', 'ignore': 'ignore me'},
                                         {'id': 11, 'name': 'name', 'ignore': 'ignore me'}]
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.echo = Mock(return_value=1)

        util.echo_list(response, ['id', 'name'])
        click_echo.echo.assert_called_with('id: 11, name: name')

    def test_echo_list_one(self, requests_mock, f_parse_response):
        requests_mock.get(self.request_url, text=self.response_text)
        f_parse_response.return_value = {'id': 10, 'name': 'name', 'ignore': 'ignore me'}
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.echo = Mock(return_value=1)

        util.echo_list(response, ['id', 'name'])
        click_echo.echo.assert_called_with('id: 10, name: name')

    def test_echo_list_pager(self, requests_mock, f_parse_response):
        requests_mock.get(self.request_url, text=self.response_text)
        f_parse_response.return_value = [{'id': 10, 'ignore': 'ignore me'}]
        response = requests.get(self.request_url)
        click_echo = click
        click_echo.echo_via_pager = Mock(return_value=1)

        util.echo_list(response, ['id', 'name'], True)
        click_echo.echo_via_pager.assert_called_with(['id: 10, name: None'])

    @staticmethod
    def test_echo_list_connection_error():
        response = 'err'
        click_echo = click
        click_echo.secho = Mock(return_value=1)

        util.echo_list(response, ['ignore'])
        click_echo.secho.assert_called_with('err', fg='red')

    def test_echo_list_one_error(self, requests_mock, f_parse_response):
        requests_mock.get(self.request_url, text=self.response_text, status_code=500, reason='test')
        f_parse_response.return_value = 'err'
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.echo = Mock(return_value=1)

        util.echo_list(response, ['ignore'])
        click_echo.echo.assert_called_with('\x1b[31merr\x1b[0m (test)')

    def test_get_yaml(self, requests_mock, f_parse_response, f_save_yaml_to_file):
        requests_mock.get(self.request_url, text=self.response_text)
        f_parse_response.return_value = {"detail": {"report": {}}}
        f_save_yaml_to_file.return_value = 'file-location'
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.secho = Mock(return_value=1)

        util.get_yaml(response, '/tmp', 'test')
        click_echo.secho.assert_called_with('Successfully saved file to file-location', fg='green')

    def test_get_yaml_echo_only(self, requests_mock, f_parse_response, f_save_yaml_to_file):
        requests_mock.get(self.request_url, text=self.response_text)
        f_parse_response.return_value = {"detail": {"report": {}}}
        f_save_yaml_to_file.return_value = 'file-location'
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.echo = Mock(return_value=1)

        util.get_yaml(response, '', '', True)
        click_echo.echo.assert_called_once()

    def test_get_yaml_echo_only_less(self, requests_mock, f_parse_response, f_save_yaml_to_file,
                                     f_format_report, mocker):
        mocker.patch(self.path + '.format_report')
        requests_mock.get(self.request_url, text=self.response_text)
        f_parse_response.return_value = {"detail": {"report": {}}}
        f_save_yaml_to_file.return_value = 'file-location'
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.echo_via_pager = Mock(return_value=1)

        util.get_yaml(response, '', '', True, True, True)
        click_echo.echo_via_pager.assert_called_once()

    def test_get_yaml_debug(self, requests_mock):
        requests_mock.get(self.request_url, text=self.response_text)
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.echo = Mock(return_value=1)

        util.get_yaml(response, '', '', True, debug=True)
        click_echo.echo.assert_called_once_with(self.response_text)

    def test_get_yaml_save_error(self, requests_mock, f_parse_response, f_save_yaml_to_file):
        requests_mock.get(self.request_url, text=self.response_text)
        f_parse_response.return_value = {"detail": {"report": {}}}
        f_save_yaml_to_file.side_effect = IOError("save error")
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.secho = Mock(return_value=1)

        util.get_yaml(response, '/tmp', 'test')
        click_echo.secho.assert_called_with('save error', fg='red')

    def test_get_yaml_request_error(self, requests_mock, f_parse_response):
        requests_mock.get(self.request_url, text=self.response_text, status_code=500, reason='test')
        f_parse_response.return_value = 'err'
        response = requests.get(self.request_url)

        click_echo = click
        click_echo.echo = Mock(return_value=1)

        util.get_yaml(response, '/tmp', 'test')
        click_echo.echo.assert_called_with('\x1b[31merr\x1b[0m (test)')

    @staticmethod
    def test_get_yaml_connection_error():
        response = 'err'
        click_echo = click
        click_echo.secho = Mock(return_value=1)

        util.get_yaml(response, '/tmp', 'test')
        click_echo.secho.assert_called_with('err', fg='red')

    def test_format_report(self, mocker):
        mock_convert_from_utc = mocker.patch(self.path + '.convert_from_utc')
        mock_convert_from_utc.return_value = 'test'
        report = {
            'pause_time': '2020-1-1T1:1:1.1',
            'plan_executions': [
                {'pause_time': '2020-1-1T1:1:1.1',
                 'stage_executions': [{
                     'pause_time': '2020-1-1T1:1:1.1',
                     'step_executions': [{
                         'pause_time': '2020-1-1T1:1:1.1',
                     }]
                 }]}
            ]
        }

        localized_report = {
            'pause_time': 'test',
            'plan_executions': [
                {'pause_time': 'test',
                 'stage_executions': [{
                     'pause_time': 'test',
                     'step_executions': [{
                         'pause_time': 'test',
                     }]
                 }]}
            ]
        }

        util.format_report(report, True)
        assert report == localized_report

    def test_format_result_line(self):
        result = util.format_result_line({"a": "one", "b": "two"}, [], False)

        assert result == "a: one, b: two"

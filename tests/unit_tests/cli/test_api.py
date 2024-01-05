from unittest.mock import Mock
import requests

from cryton.cli.utility import helpers


class TestApi:
    path = 'cryton_cli.lib.util.api'
    response_text = '{"detail": "response"}'
    address = 'http://test:8000/'
    address_ssl = 'https://test:8000/'
    address_tail = 'test/'
    address_full = address + address_tail

    def test_create_rest_api_url(self):
        result = helpers.create_rest_api_url('test', 8000, False)

        assert self.address == result

    def test_create_rest_api_url_ssl(self):
        result = helpers.create_rest_api_url('test', 8000, True)

        assert self.address_ssl == result

    def test_request_post(self, requests_mock):
        requests_mock.post(self.address_full, text=self.response_text)

        result = helpers.post_request(self.address, self.address_tail, 1)

        assert self.response_text == result.text

    def test_request_get(self, requests_mock):
        requests_mock.get(self.address_full, text=self.response_text)

        result = helpers.get_request(self.address, self.address_tail, 1)

        assert self.response_text == result.text

    def test_request_delete(self, requests_mock):
        requests_mock.delete(self.address_full, text=self.response_text)

        result = helpers.delete_request(self.address, self.address_tail, 1)

        assert self.response_text == result.text

    def test_request_post_conn_err(self, mocker):
        mock_request = mocker.patch(self.path + '.requests.post')
        mock_request.side_effect = Mock(side_effect=requests.exceptions.ConnectionError)

        result = helpers.post_request(self.address_full, self.address_tail, 1)

        assert self.address in result

    def test_request_get_conn_err(self, mocker):
        mock_request = mocker.patch(self.path + '.requests.get')
        mock_request.side_effect = Mock(side_effect=requests.exceptions.ConnectionError)

        result = helpers.get_request(self.address_full, self.address_tail, 1)

        assert self.address in result

    def test_request_delete_conn_err(self, mocker):
        mock_request = mocker.patch(self.path + '.requests.delete')
        mock_request.side_effect = Mock(side_effect=requests.exceptions.ConnectionError)

        result = helpers.delete_request(self.address_full, self.address_tail, 1)

        assert self.address in result

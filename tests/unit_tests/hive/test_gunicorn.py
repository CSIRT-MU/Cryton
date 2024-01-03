import pytest
from unittest.mock import Mock, patch

from cryton_core.lib.util import logger
from cryton_core.cryton_app.management.commands import startgunicorn


@patch('cryton_core.lib.util.logger.logger', logger.structlog.getLogger('cryton-core-test'))
class TestGunicornApplication:
    path = "cryton_core.lib.services.gunicorn"

    @pytest.fixture
    def f_altered_gunicorn_application(self):
        return startgunicorn.GunicornApplication(Mock(), {"workers": 2})

    def test___init__(self):
        mock_app = Mock()
        mock_options = {"workers": 2}

        gunicorn_application = startgunicorn.GunicornApplication(mock_app, mock_options)

        assert gunicorn_application.application == mock_app
        assert gunicorn_application.options == mock_options
        assert gunicorn_application.cfg.settings["workers"].value == mock_options["workers"]

    def test_init(self, f_altered_gunicorn_application):
        f_altered_gunicorn_application.init(Mock(), Mock(), Mock())

    def test_load(self, f_altered_gunicorn_application):
        mock_app = Mock()

        f_altered_gunicorn_application.application = mock_app

        result = f_altered_gunicorn_application.load()

        assert result == mock_app

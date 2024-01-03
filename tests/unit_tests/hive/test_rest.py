import os

import pytz
import yaml
from io import BytesIO
from datetime import datetime

from model_bakery import baker
import pytest
from unittest.mock import Mock, patch
from pytest_mock import MockerFixture
from django.test.client import Client
from django.utils.datastructures import MultiValueDict

from cryton_core.cryton_app.models import PlanExecutionModel, ExecutionVariableModel, PlanTemplateModel, PlanModel, \
    RunModel, StageExecutionModel, StageModel, StepExecutionModel, StepModel, WorkerModel
from cryton_core.cryton_app import util, exceptions
from cryton_core.lib.util import logger, exceptions as core_exceptions, states


TESTS_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


@pytest.mark.django_db
@patch('cryton_core.lib.util.logger.logger', logger.structlog.getLogger('cryton-core-test'))
class TestExecutionVariableViews:
    path = "cryton_core.cryton_app.views.execution_variable_views"
    client = Client()

    @pytest.fixture
    def f_plan_execution_model(self):
        return baker.make(PlanExecutionModel)

    @pytest.fixture
    def f_get_inventory_variables_from_files(self, mocker) -> Mock:
        return mocker.patch(self.path + ".util.get_inventory_variables_from_files")

    @pytest.fixture
    def f_execution_variable_model(self):
        return baker.make(ExecutionVariableModel)

    def test_create(self, f_plan_execution_model, f_get_inventory_variables_from_files):
        file1, file2 = BytesIO(b'{"test": "test"}'), BytesIO(b'{"test": "test"}')
        data = {'plan_execution_id': f_plan_execution_model.id, 'file': file1, 'file2': file2}

        f_get_inventory_variables_from_files.return_value = {"test": "test"}

        response = self.client.post("/api/execution_variables/", data, format='multipart')

        assert response.status_code == 201

    @pytest.mark.parametrize(
        "p_response_code, p_request_data",
        [
            (400, {'plan_execution_id': "a"}),
            (400, {'plan_execution_id': None}),
            (400, {}),
            (404, {'plan_execution_id': 1}),
        ]
    )
    def test_create_wrong_id_input(self, p_request_data, p_response_code):
        response = self.client.post("/api/execution_variables/", p_request_data, format='multipart',
                                    content_type='application/json')

        assert response.status_code == p_response_code

    def test_create_wrong_file_input(self, f_plan_execution_model, f_get_inventory_variables_from_files):
        file = BytesIO(b'')
        data = {'plan_execution_id': f_plan_execution_model.id, 'file': file}

        f_get_inventory_variables_from_files.side_effect = exceptions.ValidationError

        response = self.client.post("/api/execution_variables/", data, format='multipart')

        assert response.status_code == 400

    def test_destroy(self, f_execution_variable_model):
        response = self.client.delete(f"/api/execution_variables/{f_execution_variable_model.id}/")

        assert response.status_code == 204
        assert response.data is None

    def test_destroy_not_found(self):
        response = self.client.delete(f"/api/execution_variables/{1}/")

        assert response.status_code == 404

    def test_list(self, f_execution_variable_model):
        response = self.client.get(f"/api/execution_variables/")

        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_with_limit(self, f_execution_variable_model):
        response = self.client.get(f"/api/execution_variables/", {'limit': 10})

        assert response.status_code == 200
        assert response.data.get("count") == 1

    def test_retrieve(self, f_execution_variable_model):
        response = self.client.get(f"/api/execution_variables/{f_execution_variable_model.id}/")

        assert response.status_code == 200
        assert response.data.get("id") == f_execution_variable_model.id


@pytest.mark.django_db
@patch('cryton_core.lib.util.logger.logger', logger.structlog.getLogger('cryton-core-test'))
class TestLogViews:
    path = "cryton_core.cryton_app.views.log_views"
    client = Client()

    @pytest.fixture
    def f_get_logs(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".core_util.get_logs")

    @pytest.mark.parametrize(
        "p_request_parameters, p_get_logs_offset, p_get_logs_limit, p_get_logs_filter_parameters",
        [
            ({}, 0, 0, []),
            ({"filter": "", "offset": 0, "limit": 0}, 0, 0, []),
            ({"filter": "a", "offset": 1, "limit": 1}, 1, 1, ["a"]),
            ({"filter": "a|b", "offset": 1, "limit": 1}, 1, 1, ["a", "b"])
        ]
    )
    def test_list(self, f_get_logs, p_request_parameters: dict, p_get_logs_offset: int, p_get_logs_limit: int,
                  p_get_logs_filter_parameters: list):
        f_get_logs.return_value = [{}]

        response = self.client.get("/api/logs/", p_request_parameters)

        f_get_logs.assert_called_with(p_get_logs_offset, p_get_logs_limit, p_get_logs_filter_parameters)
        assert response.status_code == 200
        assert response.data == {'count': 1, 'next': '', 'previous': '', 'results': [{}]}

    @pytest.mark.parametrize(
        "p_request_parameters",
        [
            {"filter": "", "offset": "", "limit": 1},
            {"filter": "", "offset": 1, "limit": ""},
            {"filter": "", "offset": -1, "limit": 1},
            {"filter": "", "offset": 1, "limit": -1}
        ]
    )
    def test_list_wrong_parameters(self, p_request_parameters: dict):
        response = self.client.get("/api/logs/", p_request_parameters)

        assert response.status_code == 400


@pytest.mark.django_db
@patch('cryton_core.lib.util.logger.logger', logger.structlog.getLogger('cryton-core-test'))
class TestPlanExecutionViews:
    path = "cryton_core.cryton_app.views.plan_execution_views"
    client = Client()

    @pytest.fixture
    def f_plan_execution_model(self):
        return baker.make(PlanExecutionModel)

    @pytest.fixture
    def f_plan_execution(self, mocker) -> Mock:
        return mocker.patch(self.path + ".PlanExecution")

    def test_destroy(self, f_plan_execution):
        response = self.client.delete(f"/api/plan_executions/{1}/")

        assert response.status_code == 204
        assert response.data is None

    def test_destroy_not_found(self, f_plan_execution):
        f_plan_execution.side_effect = core_exceptions.PlanExecutionDoesNotExist

        response = self.client.delete(f"/api/plan_executions/{1}/")

        assert response.status_code == 404

    def test_list(self, f_plan_execution_model):
        response = self.client.get(f"/api/plan_executions/")

        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_with_limit(self, f_plan_execution_model):
        response = self.client.get(f"/api/plan_executions/", {'limit': 10})

        assert response.status_code == 200
        assert response.data.get("count") == 1

    def test_retrieve(self, f_plan_execution_model):
        response = self.client.get(f"/api/plan_executions/{f_plan_execution_model.id}/")

        assert response.status_code == 200
        assert response.data.get("id") == f_plan_execution_model.id

    def test_pause(self, f_plan_execution):
        response = self.client.post(f"/api/plan_executions/{1}/pause/")

        assert response.status_code == 200

    def test_pause_not_found(self, f_plan_execution):
        f_plan_execution.side_effect = core_exceptions.PlanExecutionDoesNotExist

        response = self.client.post(f"/api/plan_executions/{1}/pause/")

        assert response.status_code == 404

    def test_pause_invalid_state(self, f_plan_execution):
        f_plan_execution.return_value.pause.side_effect = core_exceptions.InvalidStateError("", 1, "", [])

        response = self.client.post(f"/api/plan_executions/{1}/pause/")

        assert response.status_code == 400

    def test_unpause(self, f_plan_execution):
        response = self.client.post(f"/api/plan_executions/{1}/unpause/")

        assert response.status_code == 200

    def test_unpause_not_found(self, f_plan_execution):
        f_plan_execution.side_effect = core_exceptions.PlanExecutionDoesNotExist

        response = self.client.post(f"/api/plan_executions/{1}/unpause/")

        assert response.status_code == 404

    def test_unpause_invalid_state(self, f_plan_execution):
        f_plan_execution.return_value.unpause.side_effect = core_exceptions.InvalidStateError("", 1, "", [])

        response = self.client.post(f"/api/plan_executions/{1}/unpause/")

        assert response.status_code == 400

    def test_report(self, f_plan_execution):
        f_plan_execution.return_value.report.return_value = {}

        response = self.client.get(f"/api/plan_executions/{1}/report/")

        assert response.status_code == 200

    def test_report_not_found(self, f_plan_execution):
        f_plan_execution.side_effect = core_exceptions.PlanExecutionDoesNotExist

        response = self.client.get(f"/api/plan_executions/{1}/report/")

        assert response.status_code == 404

    def test_validate_modules(self, f_plan_execution):
        response = self.client.post(f"/api/plan_executions/{1}/validate_modules/")

        assert response.status_code == 200

    def test_validate_modules_not_found(self, f_plan_execution):
        f_plan_execution.side_effect = core_exceptions.PlanExecutionDoesNotExist

        response = self.client.post(f"/api/plan_executions/{1}/validate_modules/")

        assert response.status_code == 404

    def test_validate_modules_rpc_timeout(self, f_plan_execution):
        f_plan_execution.return_value.validate_modules.side_effect = core_exceptions.RpcTimeoutError("")

        response = self.client.post(f"/api/plan_executions/{1}/validate_modules/")

        assert response.status_code == 500

    def test_kill(self, f_plan_execution):
        response = self.client.post(f"/api/plan_executions/{1}/kill/")

        assert response.status_code == 200

    def test_kill_not_found(self, f_plan_execution):
        f_plan_execution.side_effect = core_exceptions.PlanExecutionDoesNotExist

        response = self.client.post(f"/api/plan_executions/{1}/kill/")

        assert response.status_code == 404

    def test_kill_invalid_state(self, f_plan_execution):
        f_plan_execution.return_value.kill.side_effect = core_exceptions.InvalidStateError("", 1, "", [])

        response = self.client.post(f"/api/plan_executions/{1}/kill/")

        assert response.status_code == 400


@pytest.mark.django_db
@patch('cryton_core.lib.util.logger.logger', logger.structlog.getLogger('cryton-core-test'))
class TestPlanTemplateViews:
    path = "cryton_core.cryton_app.views.plan_template_views"
    client = Client()

    @pytest.fixture
    def f_template_model(self):
        return baker.make(PlanTemplateModel, file="tmp")

    def test_create(self):
        file = BytesIO(b'test')
        data = {'file': file}

        response = self.client.post("/api/templates/", data, format='multipart')

        assert response.status_code == 201

    def test_destroy(self, f_template_model):
        response = self.client.delete(f"/api/templates/{f_template_model.id}/")

        assert response.status_code == 204
        assert response.data is None

    def test_destroy_not_found(self):
        response = self.client.delete(f"/api/templates/{1}/")

        assert response.status_code == 404

    def test_list(self, f_template_model):
        response = self.client.get(f"/api/templates/")

        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_with_limit(self, f_template_model):
        response = self.client.get(f"/api/templates/", {'limit': 10})

        assert response.status_code == 200
        assert response.data.get("count") == 1

    def test_retrieve(self, f_template_model):
        response = self.client.get(f"/api/templates/{f_template_model.id}/")

        assert response.status_code == 200
        assert response.data.get("id") == f_template_model.id

    @pytest.mark.parametrize(
        "p_response_code, p_mock_read_data",
        [
            (200, ""),
            (200, "{{ test }}")
        ]
    )
    def test_get_template(self, f_template_model, mocker, p_response_code, p_mock_read_data):
        mocker.patch("builtins.open", mocker.mock_open(read_data=p_mock_read_data))

        response = self.client.get(f"/api/templates/{f_template_model.id}/get_template/")

        assert response.status_code == p_response_code

    def test_get_template_io_error(self, f_template_model, mocker):
        mocker.patch("builtins.open", Mock(side_effect=IOError))

        response = self.client.get(f"/api/templates/{f_template_model.id}/get_template/")

        assert response.status_code == 500

    def test_get_template_not_found(self):
        response = self.client.get(f"/api/templates/{1}/get_template/")

        assert response.status_code == 404


@pytest.mark.django_db
@patch('cryton_core.lib.util.logger.logger', logger.structlog.getLogger('cryton-core-test'))
class TestPlanViews:
    path = "cryton_core.cryton_app.views.plan_views"
    client = Client()

    @pytest.fixture
    def f_plan_model(self):
        return baker.make(PlanModel)

    @pytest.fixture
    def f_template_model(self):
        return baker.make(PlanTemplateModel, file="tmp")

    @pytest.fixture
    def f_plan(self, mocker) -> Mock:
        return mocker.patch(self.path + ".Plan")

    @pytest.fixture
    def f_create_plan(self, mocker) -> Mock:
        return mocker.patch(self.path + ".creator.create_plan")

    @pytest.fixture
    def f_fill_template(self, mocker) -> Mock:
        mock_fill_template: Mock = mocker.patch(self.path + ".util.fill_template")
        return mock_fill_template

    @pytest.fixture
    def f_get_inventory_variables_from_files(self, mocker) -> Mock:
        mock_fill_template: Mock = mocker.patch(self.path + ".util.get_inventory_variables_from_files")
        return mock_fill_template

    @pytest.fixture
    def f_parse_object_from_files(self, mocker) -> Mock:
        mock_parse_object_from_files: Mock = mocker.patch(self.path + ".util.parse_object_from_files")
        return mock_parse_object_from_files

    def test_create(self, f_template_model, f_get_inventory_variables_from_files, f_create_plan, mocker,
                    f_fill_template):
        file, inventory_file = BytesIO(b'{"plan": "test"}'), BytesIO(b'{"test": "test"}')
        data = {'template_id': f_template_model.id, 'file': file, 'inventory_file': inventory_file}

        mocker.patch("builtins.open", mocker.mock_open(read_data=""))
        f_fill_template.return_value = '{"plan": "test"}'
        f_get_inventory_variables_from_files.return_value = {}
        f_create_plan.return_value = 1

        response = self.client.post("/api/plans/", data, format='multipart')

        assert response.status_code == 201

    @pytest.mark.parametrize(
        "p_response_code, p_request_data",
        [
            (400, {'template_id': "a"}),
            (400, {'template_id': None}),
            (400, {}),
            (404, {'template_id': 1}),
        ]
    )
    def test_create_wrong_template_id(self, p_request_data, p_response_code):
        response = self.client.post("/api/plans/", p_request_data, format='multipart', content_type='application/json')

        assert response.status_code == p_response_code

    @pytest.mark.parametrize(
        "p_fill_template, p_parse_inventory_file, p_create_plan, p_yaml_load",
        [
            ("", exceptions.ValidationError, 1, ""),
            (exceptions.ValidationError, {"test": "test"}, 1, {"plan": "test"}),
            ("", {"plan": "test"}, 1, yaml.YAMLError),
            ("", {"plan": "test"}, core_exceptions.ValidationError(""), {"plan": "test"}),
            ("", {"plan": "test"}, core_exceptions.CreationFailedError({}), {"plan": "test"}),
            ("", "", 1, ""),
            ("", {"no-plan-parameter": "test"}, 1, {"no-plan-parameter": "test"}),
        ]
    )
    def test_create_error(self, f_template_model, f_get_inventory_variables_from_files, f_create_plan, mocker,
                          f_fill_template, p_fill_template, p_parse_inventory_file, p_create_plan, p_yaml_load):
        file, inventory_file = BytesIO(b'{"test": "test"}'), BytesIO(b'{"test": "test"}')
        data = {'template_id': f_template_model.id, 'file': file, 'inventory_file': inventory_file}

        mocker.patch("builtins.open", mocker.mock_open(read_data=""))
        mocker.patch("yaml.safe_load", Mock(side_effect=[p_yaml_load]))
        f_fill_template.side_effect = [p_fill_template]
        f_get_inventory_variables_from_files.side_effect = [p_parse_inventory_file]
        f_create_plan.side_effect = [p_create_plan]

        response = self.client.post("/api/plans/", data, format='multipart')

        assert response.status_code == 400

    def test_destroy(self, f_plan):
        response = self.client.delete(f"/api/plans/{1}/")

        assert response.status_code == 204
        assert response.data is None

    def test_destroy_not_found(self, f_plan):
        f_plan.side_effect = core_exceptions.PlanObjectDoesNotExist

        response = self.client.delete(f"/api/plans/{1}/")

        assert response.status_code == 404

    def test_list(self, f_plan_model):
        response = self.client.get(f"/api/plans/")

        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_with_limit(self, f_plan_model):
        response = self.client.get(f"/api/plans/", {'limit': 10})

        assert response.status_code == 200
        assert response.data.get("count") == 1

    def test_retrieve(self, f_plan_model):
        response = self.client.get(f"/api/plans/{f_plan_model.id}/")

        assert response.status_code == 200
        assert response.data.get("id") == f_plan_model.id

    @pytest.mark.parametrize(
        "p_plan_validate, p_response_code",
        [
            (Mock(), 200),
            (AttributeError, 400),
            (core_exceptions.ValidationError(""), 400),
        ]
    )
    def test_validate(self, f_plan, p_plan_validate, p_response_code, f_parse_object_from_files):
        f_parse_object_from_files.return_value = {'plan': {}}
        f_plan.validate.side_effect = p_plan_validate

        response = self.client.post(f"/api/plans/validate/", {}, content_type='application/json')

        assert response.status_code == p_response_code

    @pytest.mark.parametrize(
        "p_request_data, p_plan_exists, p_worker_exists, p_run_exists, p_response_code, p_run_state, p_run_plan_id",
        [
            ({"run_id": 1, "worker_id": 1}, True, True, True, 200, states.RUNNING, 1),
            ({"run_id": 1, "worker_id": 1}, True, True, True, 200, states.FINISHED, 1),
            ({"run_id": 1}, True, True, True, 400, states.RUNNING, 1),
            ({"worker_id": 1}, True, True, True, 400, states.RUNNING, 1),
            ({"run_id": "test", "worker_id": 1}, True, True, True, 400, states.RUNNING, 1),
            ({"run_id": 1, "worker_id": "test"}, True, True, True, 400, states.RUNNING, 1),
            ({"run_id": None, "worker_id": 1}, True, True, True, 400, states.RUNNING, 1),
            ({"run_id": 1, "worker_id": None}, True, True, True, 400, states.RUNNING, 1),
            ({"run_id": 1, "worker_id": 1}, False, True, True, 400, states.RUNNING, 1),
            ({"run_id": 1, "worker_id": 1}, True, False, True, 400, states.RUNNING, 1),
            ({"run_id": 1, "worker_id": 1}, True, True, False, 400, states.RUNNING, 1),
            ({"run_id": 1, "worker_id": 1}, True, True, True, 400, states.PENDING, 1),
            ({"run_id": 1, "worker_id": 1}, True, True, True, 400, states.RUNNING, 2),
        ]
    )
    def test_execute(self, f_plan, mocker, p_request_data, p_plan_exists, p_worker_exists,
                     p_run_exists, p_response_code, p_run_state, p_run_plan_id):
        mock_plan_filter: Mock = mocker.patch(self.path + ".PlanModel.objects.filter")
        mock_plan_filter.return_value.exists.return_value = p_plan_exists
        mock_worker_filter: Mock = mocker.patch(self.path + ".WorkerModel.objects.filter")
        mock_worker_filter.return_value.exists.return_value = p_worker_exists
        mock_run_filter: Mock = mocker.patch(self.path + ".RunModel.objects.filter")
        mock_run_filter.return_value.exists.return_value = p_run_exists
        mock_run = mocker.patch(self.path + ".Run")
        mock_run.return_value.model.plan_model.id = p_run_plan_id
        mock_run.return_value.state = p_run_state
        mocker.patch(self.path + ".PlanExecution")

        response = self.client.post(f"/api/plans/{1}/execute/", p_request_data, content_type='application/json')

        assert response.status_code == p_response_code

    def test_get_plan(self, f_plan_model):
        f_plan_model.plan = {}

        response = self.client.get(f"/api/plans/{f_plan_model.id}/get_plan/")

        assert response.status_code == 200

    def test_get_plan_non_existent(self):
        response = self.client.get(f"/api/plans/{0}/get_plan/")

        assert response.status_code == 404


@pytest.mark.django_db
@patch('cryton_core.lib.util.logger.logger', logger.structlog.getLogger('cryton-core-test'))
class TestRunViews:
    path = "cryton_core.cryton_app.views.run_views"
    client = Client()

    @pytest.fixture
    def f_run_model(self):
        return baker.make(RunModel)

    @pytest.fixture
    def f_run(self, mocker) -> Mock:
        return mocker.patch(self.path + ".Run")

    def test_create(self, mocker, f_run):
        data = {"plan_id": 1, "worker_ids": [baker.make(WorkerModel).id, baker.make(WorkerModel).id]}

        f_run.return_value.model.id = 1
        f_run.return_value.model.plan_executions.values_list.return_value = [0, 1]
        mocker.patch(self.path + ".PlanModel")

        response = self.client.post(f"/api/runs/", data, content_type='application/json')

        assert response.status_code == 201

    @pytest.mark.parametrize(
        "p_plan_id, p_worker_ids",
        [
            ("", [1]),
            (None, [1]),
            (1, []),
            (1, None),
            (1, "1"),
            (1, 1),
            (1, ["1"]),
        ]
    )
    def test_create_wrong_input(self, p_plan_id, p_worker_ids):
        data = {"plan_id": p_plan_id, "worker_ids": p_worker_ids}

        response = self.client.post(f"/api/runs/", data, content_type='application/json')

        assert response.status_code == 400

    def test_create_nonexistent_plan(self):
        data = {"plan_id": 1, "worker_ids": [baker.make(WorkerModel).id]}

        response = self.client.post(f"/api/runs/", data, content_type='application/json')

        assert response.status_code == 404

    def test_destroy(self, f_run):
        response = self.client.delete(f"/api/runs/{1}/")

        assert response.status_code == 204
        assert response.data is None

    def test_destroy_not_found(self, f_run):
        f_run.side_effect = core_exceptions.RunObjectDoesNotExist

        response = self.client.delete(f"/api/runs/{1}/")

        assert response.status_code == 404

    def test_list(self, f_run_model):
        response = self.client.get(f"/api/runs/")

        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_with_limit(self, f_run_model):
        response = self.client.get(f"/api/runs/", {'limit': 10})

        assert response.status_code == 200
        assert response.data.get("count") == 1

    def test_retrieve(self, f_run_model):
        response = self.client.get(f"/api/runs/{f_run_model.id}/")

        assert response.status_code == 200
        assert response.data.get("id") == f_run_model.id

    def test_report(self, f_run):
        f_run.return_value.report.return_value = {}

        response = self.client.get(f"/api/runs/{1}/report/")

        assert response.status_code == 200

    def test_report_not_found(self, f_run):
        f_run.side_effect = core_exceptions.RunObjectDoesNotExist

        response = self.client.get(f"/api/runs/{1}/report/")

        assert response.status_code == 404

    @pytest.mark.parametrize(
        "p_run_effect, p_response_code",
        [
            (Mock(), 200),
            (core_exceptions.InvalidStateError("", 1, "", []), 400),
            (core_exceptions.RunObjectDoesNotExist, 404)
        ]
    )
    def test_pause(self, f_run, p_run_effect, p_response_code):
        f_run.side_effect = p_run_effect

        response = self.client.post(f"/api/runs/{1}/pause/")

        assert response.status_code == p_response_code

    @pytest.mark.parametrize(
        "p_run_effect, p_response_code",
        [
            (Mock(), 200),
            (core_exceptions.InvalidStateError("", 1, "", []), 400),
            (core_exceptions.RunObjectDoesNotExist, 404)
        ]
    )
    def test_unpause(self, f_run, p_run_effect, p_response_code):
        f_run.side_effect = p_run_effect

        response = self.client.post(f"/api/runs/{1}/unpause/")

        assert response.status_code == p_response_code

    @pytest.mark.parametrize(
        "p_run_effect, p_response_code",
        [
            (Mock(), 200),
            (core_exceptions.InvalidStateError("", 1, "", []), 400),
            (core_exceptions.RunObjectDoesNotExist, 404)
        ]
    )
    def test_schedule(self, f_run, mocker, p_run_effect, p_response_code):
        f_run.side_effect = p_run_effect
        mocker.patch(self.path + ".util.get_start_time")

        response = self.client.post(f"/api/runs/{1}/schedule/")

        assert response.status_code == p_response_code

    @pytest.mark.parametrize(
        "p_run_state, p_response_code",
        [
            (states.PENDING, 200),
            (states.FINISHED, 400),
        ]
    )
    def test_execute(self, f_run, p_run_state, p_response_code):
        f_run.return_value.state = p_run_state

        response = self.client.post(f"/api/runs/{1}/execute/")

        assert response.status_code == p_response_code

    def test_execute_not_found(self, f_run):
        f_run.side_effect = core_exceptions.RunObjectDoesNotExist

        response = self.client.post(f"/api/runs/{1}/execute/")

        assert response.status_code == 404

    def test_execute_invalid_state(self, f_run):
        f_run.return_value.state = states.PENDING
        f_run.return_value.execute.side_effect = core_exceptions.InvalidStateError("", 1, "", [])

        response = self.client.post(f"/api/runs/{1}/execute/")

        assert response.status_code == 400

    def test_execute_rpc_timeout(self, f_run):
        f_run.return_value.state = states.PENDING
        f_run.return_value.execute.side_effect = core_exceptions.RpcTimeoutError("")

        response = self.client.post(f"/api/runs/{1}/execute/")

        assert response.status_code == 500

    @pytest.mark.parametrize(
        "p_run_effect, p_response_code",
        [
            (Mock(), 200),
            (core_exceptions.InvalidStateError("", 1, "", []), 400),
            (core_exceptions.RunObjectDoesNotExist, 404)
        ]
    )
    def test_reschedule(self, f_run, mocker, p_run_effect, p_response_code):
        f_run.side_effect = p_run_effect
        mocker.patch(self.path + ".util.get_start_time")

        response = self.client.post(f"/api/runs/{1}/reschedule/")

        assert response.status_code == p_response_code

    def test_postpone(self, f_run, mocker):
        data = {"delta": "1:1:1"}

        mocker.patch(self.path + ".core_util.parse_delta_to_datetime")

        response = self.client.post(f"/api/runs/{1}/postpone/", data, content_type='application/json')

        assert response.status_code == 200

    def test_postpone_not_found(self, f_run):
        f_run.side_effect = core_exceptions.RunObjectDoesNotExist

        response = self.client.post(f"/api/runs/{1}/postpone/", content_type='application/json')

        assert response.status_code == 404

    def test_postpone_delta_missing_error(self, f_run):
        response = self.client.post(f"/api/runs/{1}/postpone/", content_type='application/json')

        assert response.status_code == 400

    def test_postpone_delta_input_error(self, f_run, mocker):
        data = {"delta": "1h1m1s"}

        mocker.patch(self.path + ".core_util.parse_delta_to_datetime",
                     Mock(side_effect=core_exceptions.UserInputError("")))

        response = self.client.post(f"/api/runs/{1}/postpone/", data, content_type='application/json')

        assert response.status_code == 400

    def test_postpone_invalid_state(self, f_run, mocker):
        data = {"delta": "1h1m1s"}

        f_run.return_value.postpone.side_effect = core_exceptions.InvalidStateError("", 1, "", [])
        mocker.patch(self.path + ".core_util.parse_delta_to_datetime")

        response = self.client.post(f"/api/runs/{1}/postpone/", data, content_type='application/json')

        assert response.status_code == 400

    @pytest.mark.parametrize(
        "p_run_effect, p_response_code",
        [
            (Mock(), 200),
            (core_exceptions.InvalidStateError("", 1, "", []), 400),
            (core_exceptions.RunObjectDoesNotExist, 404)
        ]
    )
    def test_unschedule(self, f_run, mocker, p_run_effect, p_response_code):
        f_run.side_effect = p_run_effect
        mocker.patch(self.path + ".util.get_start_time")

        response = self.client.post(f"/api/runs/{1}/unschedule/")

        assert response.status_code == p_response_code

    @pytest.mark.parametrize(
        "p_run_effect, p_response_code",
        [
            (Mock(), 200),
            (core_exceptions.InvalidStateError("", 1, "", []), 400),
            (core_exceptions.RunObjectDoesNotExist, 404)
        ]
    )
    def test_kill(self, f_run, p_run_effect, p_response_code):
        f_run.side_effect = p_run_effect

        response = self.client.post(f"/api/runs/{1}/kill/")

        assert response.status_code == p_response_code

    @pytest.mark.parametrize(
        "p_run_effect, p_response_code",
        [
            (Mock(), 200),
            (core_exceptions.RunObjectDoesNotExist, 404)
        ]
    )
    def test_healthcheck_workers(self, f_run, p_run_effect, p_response_code):
        f_run.side_effect = p_run_effect

        response = self.client.post(f"/api/runs/{1}/healthcheck_workers/")

        assert response.status_code == p_response_code

    def test_healthcheck_workers_rpc_timeout(self, f_run):
        f_run.return_value.healthcheck_workers.side_effect = ConnectionError("")

        response = self.client.post(f"/api/runs/{1}/healthcheck_workers/")

        assert response.status_code == 500

    @pytest.mark.parametrize(
        "p_run_effect, p_response_code",
        [
            (Mock(), 200),
            (core_exceptions.RunObjectDoesNotExist, 404)
        ]
    )
    def test_validate_modules(self, f_run, p_run_effect, p_response_code):
        f_run.side_effect = p_run_effect

        response = self.client.post(f"/api/runs/{1}/validate_modules/")

        assert response.status_code == p_response_code

    def test_validate_modules_rpc_timeout(self, f_run):
        f_run.return_value.validate_modules.side_effect = core_exceptions.RpcTimeoutError("")

        response = self.client.post(f"/api/runs/{1}/validate_modules/")

        assert response.status_code == 500

    def test_get_plan(self, f_run_model):
        f_run_model.plan_model.plan = {}

        response = self.client.get(f"/api/runs/{f_run_model.id}/get_plan/")

        assert response.status_code == 200

    def test_get_plan_non_existent(self):
        response = self.client.get(f"/api/runs/{0}/get_plan/")

        assert response.status_code == 404


@pytest.mark.django_db
@patch('cryton_core.lib.util.logger.logger', logger.structlog.getLogger('cryton-core-test'))
class TestStageExecutionViews:
    path = "cryton_core.cryton_app.views.stage_execution_views"
    client = Client()

    @pytest.fixture
    def f_stage_execution_model(self):
        return baker.make(StageExecutionModel)

    @pytest.fixture
    def f_stage_execution(self, mocker) -> Mock:
        return mocker.patch(self.path + ".StageExecution")

    def test_destroy(self, f_stage_execution):
        response = self.client.delete(f"/api/stage_executions/{1}/")

        assert response.status_code == 204
        assert response.data is None

    def test_destroy_not_found(self, f_stage_execution):
        f_stage_execution.side_effect = core_exceptions.StageExecutionObjectDoesNotExist("")

        response = self.client.delete(f"/api/stage_executions/{1}/")

        assert response.status_code == 404

    def test_list(self, f_stage_execution_model):
        response = self.client.get(f"/api/stage_executions/")

        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_with_limit(self, f_stage_execution_model):
        response = self.client.get(f"/api/stage_executions/", {'limit': 10})

        assert response.status_code == 200
        assert response.data.get("count") == 1

    def test_retrieve(self, f_stage_execution_model):
        response = self.client.get(f"/api/stage_executions/{f_stage_execution_model.id}/")

        assert response.status_code == 200
        assert response.data.get("id") == f_stage_execution_model.id

    def test_report(self, f_stage_execution):
        f_stage_execution.return_value.report.return_value = {}

        response = self.client.get(f"/api/stage_executions/{1}/report/")

        assert response.status_code == 200

    def test_report_not_found(self, f_stage_execution):
        f_stage_execution.side_effect = core_exceptions.StageExecutionObjectDoesNotExist("")

        response = self.client.get(f"/api/stage_executions/{1}/report/")

        assert response.status_code == 404

    @pytest.mark.parametrize(
        "p_stage_execution_effect, p_response_code",
        [
            (Mock(), 200),
            (core_exceptions.InvalidStateError("", 1, "", []), 400),
            (core_exceptions.StageExecutionObjectDoesNotExist(""), 404)
        ]
    )
    def test_kill(self, f_stage_execution, p_stage_execution_effect, p_response_code):
        f_stage_execution.side_effect = p_stage_execution_effect

        response = self.client.post(f"/api/stage_executions/{1}/kill/")

        assert response.status_code == p_response_code

    @pytest.mark.parametrize(
        "p_stage_execution_effect, p_response_code",
        [
            (Mock(), 200),
            (core_exceptions.StageExecutionObjectDoesNotExist(""), 404)
        ]
    )
    def test_re_execute(self, f_stage_execution, p_stage_execution_effect, p_response_code):
        f_stage_execution.side_effect = p_stage_execution_effect

        response = self.client.post(f"/api/stage_executions/{1}/re_execute/")

        assert response.status_code == p_response_code

    def test_re_execute_invalid_input(self, f_stage_execution):
        data = {'immediately': None}

        response = self.client.post(f"/api/stage_executions/{1}/re_execute/", data, content_type='application/json')

        assert response.status_code == 400

    def test_re_execute_invalid_state(self, f_stage_execution):
        f_stage_execution.return_value.re_execute.side_effect = core_exceptions.InvalidStateError("", 1, "", [])

        response = self.client.post(f"/api/stage_executions/{1}/re_execute/")

        assert response.status_code == 400


@pytest.mark.django_db
@patch('cryton_core.lib.util.logger.logger', logger.structlog.getLogger('cryton-core-test'))
class TestStageViews:
    path = "cryton_core.cryton_app.views.stage_views"
    client = Client()

    @pytest.fixture
    def f_stage_model(self):
        return baker.make(StageModel)

    @pytest.fixture
    def f_stage(self, mocker) -> Mock:
        return mocker.patch(self.path + ".Stage")

    @pytest.fixture
    def f_create_stage(self, mocker) -> Mock:
        return mocker.patch(self.path + ".creator.create_stage")

    @pytest.fixture
    def f_parse_object_from_files(self, mocker) -> Mock:
        mock_parse_object_from_files: Mock = mocker.patch(self.path + ".util.parse_object_from_files")
        return mock_parse_object_from_files

    @pytest.fixture
    def f_stage_execution(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".StageExecution")

    @pytest.fixture
    def f_plan_execution(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".PlanExecution")

    def test_destroy(self, f_stage):
        response = self.client.delete(f"/api/stages/{1}/")

        assert response.status_code == 204
        assert response.data is None

    def test_destroy_not_found(self, f_stage):
        f_stage.side_effect = core_exceptions.StageObjectDoesNotExist("")

        response = self.client.delete(f"/api/stages/{1}/")

        assert response.status_code == 404

    def test_list(self, f_stage_model):
        response = self.client.get(f"/api/stages/")

        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_with_limit(self, f_stage_model):
        response = self.client.get(f"/api/stages/", {'limit': 10})

        assert response.status_code == 200
        assert response.data.get("count") == 1

    def test_retrieve(self, f_stage_model):
        response = self.client.get(f"/api/stages/{f_stage_model.id}/")

        assert response.status_code == 200
        assert response.data.get("id") == f_stage_model.id

    def test_create(self, f_parse_object_from_files, f_create_stage, f_stage):
        plan_model_obj = baker.make(PlanModel, dynamic=True)
        file, inventory_file = BytesIO(b'{"test": "test"}'), BytesIO(b'{"test": "test"}')
        data = {'plan_id': plan_model_obj.id, 'file': file, 'inventory_file': inventory_file}

        f_parse_object_from_files.return_value = {"name": "test_create_stage"}
        f_create_stage.return_value = 1

        response = self.client.post("/api/stages/", data, format='multipart')

        assert response.status_code == 201

    @pytest.mark.parametrize(
        "p_response_code, p_request_data",
        [
            (400, {'plan_id': "a"}),
            (400, {'plan_id': None}),
            (400, {}),
            (404, {'plan_id': 1}),
        ]
    )
    def test_create_wrong_id_input(self, p_request_data, p_response_code):
        response = self.client.post("/api/stages/", p_request_data, format='multipart', content_type='application/json')

        assert response.status_code == p_response_code

    @pytest.mark.parametrize(
        "p_parse_object_from_files, p_validate_stage, p_dynamic_plan",
        [
            ({"name": "test_create_error"}, None, False),
            (exceptions.ValidationError, None, True),
            ({"name": "test_create_error"}, core_exceptions.ValidationError(""), True),
            ({"name": "test_create_error_non_unique"}, None, True)
        ]
    )
    def test_create_error(self, f_parse_object_from_files, f_create_stage, f_stage,
                          p_parse_object_from_files, p_validate_stage, p_dynamic_plan):
        plan_model_obj = baker.make(PlanModel, dynamic=p_dynamic_plan)
        baker.make(StageModel, name="test_create_error_non_unique", plan_model=plan_model_obj)
        file1, file2 = BytesIO(b'{"test": "test"}'), BytesIO(b'{"test": "test"}')
        data = {'plan_id': plan_model_obj.id, 'file': file1, 'file2': file2}

        f_parse_object_from_files.side_effect = [p_parse_object_from_files]
        f_create_stage.return_value = 1
        f_stage.validate.side_effect = [p_validate_stage]

        response = self.client.post("/api/stages/", data, format='multipart')

        assert response.status_code == 400

    @pytest.mark.parametrize(
        "p_plan_ex_state",
        [
            states.RUNNING,
            states.FINISHED
        ]
    )
    def test_start_trigger(self, f_stage, f_stage_model, f_stage_execution, f_plan_execution, p_plan_ex_state):
        request_data = {'plan_execution_id': 1}

        f_stage.return_value.model.plan_model.id = 1
        f_plan_execution.return_value.model.plan_model.id = 1
        f_plan_execution.return_value.model.stage_executions.filter.return_value.exists.return_value = False
        f_plan_execution.return_value.state = p_plan_ex_state
        f_stage_execution.return_value.model.id = 1

        response = self.client.post(f"/api/stages/{f_stage_model.id}/start_trigger/", request_data,
                                    format='multipart',
                                    content_type='application/json')

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "p_plan_is_dynamic, p_plan_model_id, p_same_stage_exists, p_plan_ex_state",
        [
            (False, 1, False, states.RUNNING),
            (True, 2, False, states.RUNNING),
            (True, 1, True, states.RUNNING),
            (True, 1, False, states.PENDING)
        ]
    )
    def test_start_trigger_validation(self, f_stage, f_stage_model, f_stage_execution, f_plan_execution,
                                      p_plan_is_dynamic, p_plan_model_id, p_same_stage_exists, p_plan_ex_state):
        request_data = {'plan_execution_id': 1}

        f_stage.return_value.model.plan_model.id = 1
        f_stage.return_value.model.plan_model.dynamic = p_plan_is_dynamic
        f_plan_execution.return_value.model.plan_model.id = p_plan_model_id
        f_plan_execution.return_value.model.stage_executions.filter.return_value.exists\
            .return_value = p_same_stage_exists
        f_plan_execution.return_value.state = p_plan_ex_state
        f_stage_execution.return_value.model.id = 1

        response = self.client.post(f"/api/stages/{f_stage_model.id}/start_trigger/", request_data,
                                    format='multipart',
                                    content_type='application/json')

        assert response.status_code == 400

    @pytest.mark.parametrize(
        "p_response_code, p_request_data",
        [
            (400, {'plan_execution_id': "a"}),
            (400, {'plan_execution_id': None}),
            (400, {}),
            (404, {'plan_execution_id': 1}),
        ]
    )
    def test_start_trigger_wrong_plan_execution_id(self, f_stage, p_request_data, p_response_code):
        response = self.client.post("/api/stages/1/start_trigger/", p_request_data, format='multipart',
                                    content_type='application/json')

        assert response.status_code == p_response_code

    def test_start_trigger_wrong_stage_id(self):
        response = self.client.post("/api/stages/1/start_trigger/", format='multipart', content_type='application/json')

        assert response.status_code == 404

    @pytest.mark.parametrize(
        "p_stage_validate, p_response_code, p_dynamic_value",
        [
            (Mock(), 200, ""),
            (Mock(), 400, False),
            (core_exceptions.ValidationError(""), 400, ""),
        ]
    )
    def test_validate(self, f_stage, p_stage_validate, p_response_code, p_dynamic_value, f_parse_object_from_files):
        data = {"dynamic": p_dynamic_value}

        f_parse_object_from_files.return_value = {}
        f_stage.validate.side_effect = p_stage_validate

        response = self.client.post(f"/api/stages/validate/", data, content_type='application/json')

        assert response.status_code == p_response_code


@pytest.mark.django_db
@patch('cryton_core.lib.util.logger.logger', logger.structlog.getLogger('cryton-core-test'))
class TestStepExecutionViews:
    path = "cryton_core.cryton_app.views.step_execution_views"
    client = Client()

    @pytest.fixture
    def f_step_execution_model(self):
        return baker.make(StepExecutionModel)

    @pytest.fixture
    def f_step_execution(self, mocker) -> Mock:
        return mocker.patch(self.path + ".StepExecution")

    def test_destroy(self, f_step_execution):
        response = self.client.delete(f"/api/step_executions/{1}/")

        assert response.status_code == 204
        assert response.data is None

    def test_destroy_not_found(self, f_step_execution):
        f_step_execution.side_effect = core_exceptions.StepExecutionObjectDoesNotExist("")

        response = self.client.delete(f"/api/step_executions/{1}/")

        assert response.status_code == 404

    def test_list(self, f_step_execution_model):
        response = self.client.get(f"/api/step_executions/")

        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_with_limit(self, f_step_execution_model):
        response = self.client.get(f"/api/step_executions/", {'limit': 10})

        assert response.status_code == 200
        assert response.data.get("count") == 1

    def test_retrieve(self, f_step_execution_model):
        response = self.client.get(f"/api/step_executions/{f_step_execution_model.id}/")

        assert response.status_code == 200
        assert response.data.get("id") == f_step_execution_model.id

    def test_report(self, f_step_execution):
        f_step_execution.return_value.report.return_value = {}

        response = self.client.get(f"/api/step_executions/{1}/report/")

        assert response.status_code == 200

    def test_report_not_found(self, f_step_execution):
        f_step_execution.side_effect = core_exceptions.StepExecutionObjectDoesNotExist("")

        response = self.client.get(f"/api/step_executions/{1}/report/")

        assert response.status_code == 404

    @pytest.mark.parametrize(
        "p_stage_execution_effect, p_response_code",
        [
            (Mock(), 200),
            (core_exceptions.InvalidStateError("", 1, "", []), 400),
            (core_exceptions.StepExecutionObjectDoesNotExist(""), 404)
        ]
    )
    def test_kill(self, f_step_execution, p_stage_execution_effect, p_response_code):
        f_step_execution.side_effect = p_stage_execution_effect

        response = self.client.post(f"/api/step_executions/{1}/kill/")

        assert response.status_code == p_response_code

    @pytest.mark.parametrize(
        "p_stage_execution_effect, p_response_code",
        [
            (Mock(), 200),
            (core_exceptions.StepExecutionObjectDoesNotExist(""), 404)
        ]
    )
    def test_re_execute(self, f_step_execution, p_stage_execution_effect, p_response_code):
        f_step_execution.side_effect = p_stage_execution_effect

        response = self.client.post(f"/api/step_executions/{1}/re_execute/")

        assert response.status_code == p_response_code

    def test_re_execute_invalid_state(self, f_step_execution):
        f_step_execution.return_value.re_execute.side_effect = core_exceptions.InvalidStateError("", 1, "", [])

        response = self.client.post(f"/api/step_executions/{1}/re_execute/")

        assert response.status_code == 400


@pytest.mark.django_db
@patch('cryton_core.lib.util.logger.logger', logger.structlog.getLogger('cryton-core-test'))
class TestStepViews:
    path = "cryton_core.cryton_app.views.step_views"
    client = Client()

    @pytest.fixture
    def f_step_model(self):
        return baker.make(StepModel)

    @pytest.fixture
    def f_step(self, mocker) -> Mock:
        return mocker.patch(self.path + ".Step")

    @pytest.fixture
    def f_step_execution(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".StepExecution")

    @pytest.fixture
    def f_stage_execution(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".StageExecution")

    @pytest.fixture
    def f_create_step(self, mocker) -> Mock:
        return mocker.patch(self.path + ".creator.create_step")

    @pytest.fixture
    def f_parse_object_from_files(self, mocker) -> Mock:
        mock_parse_object_from_files: Mock = mocker.patch(self.path + ".util.parse_object_from_files")
        return mock_parse_object_from_files

    def test_destroy(self, f_step):
        response = self.client.delete(f"/api/steps/{1}/")

        assert response.status_code == 204
        assert response.data is None

    def test_destroy_not_found(self, f_step):
        f_step.side_effect = core_exceptions.StepObjectDoesNotExist("")

        response = self.client.delete(f"/api/steps/{1}/")

        assert response.status_code == 404

    def test_list(self, f_step_model):
        response = self.client.get(f"/api/steps/")

        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_with_limit(self, f_step_model):
        response = self.client.get(f"/api/steps/", {'limit': 10})

        assert response.status_code == 200
        assert response.data.get("count") == 1

    def test_retrieve(self, f_step_model):
        response = self.client.get(f"/api/steps/{f_step_model.id}/")

        assert response.status_code == 200
        assert response.data.get("id") == f_step_model.id

    @pytest.mark.parametrize(
        "p_step_validate, p_response_code",
        [
            (Mock(), 200),
            (core_exceptions.StepTypeDoesNotExist("", []), 400),
            (core_exceptions.ValidationError(""), 400),
        ]
    )
    def test_validate(self, f_step, p_step_validate, p_response_code, f_parse_object_from_files):
        f_parse_object_from_files.return_value = {}
        f_step.validate.side_effect = p_step_validate

        response = self.client.post(f"/api/steps/validate/", {}, content_type='application/json')

        assert response.status_code == p_response_code

    def test_create(self, f_parse_object_from_files, f_create_step, f_step, mocker):
        stage_model_obj = baker.make(StageModel, plan_model=baker.make(PlanModel, dynamic=True))
        baker.make(StepModel, stage_model=stage_model_obj)
        file, inventory_file = BytesIO(b'{"test": "test"}'), BytesIO(b'{"test": "test"}')
        data = {'stage_id': stage_model_obj.id, 'file': file, 'inventory_file': inventory_file}

        f_parse_object_from_files.return_value = {"name": "test_create_step"}
        f_create_step.return_value = 1
        mocker.patch(self.path + ".creator.create_successor")

        response = self.client.post("/api/steps/", data, format='multipart')

        assert response.status_code == 201

    @pytest.mark.parametrize(
        "p_response_code, p_request_data",
        [
            (400, {'stage_id': "a"}),
            (400, {'stage_id': None}),
            (400, {}),
            (404, {'stage_id': 1}),
        ]
    )
    def test_create_wrong_id_input(self, p_request_data, p_response_code):
        response = self.client.post("/api/steps/", p_request_data, format='multipart', content_type='application/json')

        assert response.status_code == p_response_code

    @pytest.mark.parametrize(
        "p_parse_object_from_files, p_validate_step, p_dynamic_plan",
        [
            ({"name": "test_create_error"}, None, False),
            (exceptions.ValidationError, None, True),
            ({"name": "test_create_error"}, core_exceptions.ValidationError(""), True),
            ({"name": "test_create_error_non_unique"}, None, True)
        ]
    )
    def test_create_error(self, f_parse_object_from_files, f_create_step, f_step,
                          p_parse_object_from_files, p_validate_step, p_dynamic_plan):
        stage_model_obj = baker.make(StageModel, plan_model=baker.make(PlanModel, dynamic=p_dynamic_plan))
        baker.make(StepModel, name="test_create_error_non_unique", stage_model=stage_model_obj)
        file1, file2 = BytesIO(b'{"test": "test"}'), BytesIO(b'{"test": "test"}')
        data = {'stage_id': stage_model_obj.id, 'file': file1, 'file2': file2}

        f_parse_object_from_files.side_effect = [p_parse_object_from_files]
        f_create_step.return_value = 1
        f_step.validate.side_effect = [p_validate_step]

        response = self.client.post("/api/steps/", data, format='multipart')

        assert response.status_code == 400

    @pytest.mark.parametrize(
        "p_stage_ex_state",
        [
            states.RUNNING,
            states.FINISHED
        ]
    )
    def test_execute(self, f_step, f_step_model, f_step_execution, f_stage_execution, mocker, p_stage_ex_state):
        request_data = {'stage_execution_id': 1}

        f_step_execution.return_value.model.id = 1
        f_step.return_value.model.stage_model.id = 1
        mocker.patch(self.path + ".StepExecutionType")
        f_stage_execution.return_value.model.stage_model.id = 1
        f_stage_execution.return_value.model.step_executions.filter.return_value.exists.return_value = False
        f_stage_execution.return_value.state = p_stage_ex_state

        response = self.client.post(f"/api/steps/{f_step_model.id}/execute/", request_data,
                                    format='multipart',
                                    content_type='application/json')

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "p_plan_is_dynamic, p_stage_model_id, p_same_step_exists, p_stage_ex_state",
        [
            (False, 1, False, states.RUNNING),
            (True, 2, False, states.RUNNING),
            (True, 1, True, states.RUNNING),
            (True, 1, False, states.PENDING)
        ]
    )
    def test_execute_validation(self, f_step, f_step_model, f_step_execution, f_stage_execution,
                                p_plan_is_dynamic, p_stage_model_id, p_same_step_exists, p_stage_ex_state):
        request_data = {'stage_execution_id': 1}

        f_step_execution.return_value.model.id = 1
        f_step.return_value.model.stage_model.id = 1
        f_step.return_value.model.stage_model.plan_model.dynamic = p_plan_is_dynamic
        f_stage_execution.return_value.model.stage_model.id = p_stage_model_id
        f_stage_execution.return_value.model.step_executions.filter.return_value.exists\
            .return_value = p_same_step_exists
        f_stage_execution.return_value.state = p_stage_ex_state

        response = self.client.post(f"/api/steps/{f_step_model.id}/execute/", request_data,
                                    format='multipart',
                                    content_type='application/json')

        assert response.status_code == 400

    @pytest.mark.parametrize(
        "p_response_code, p_request_data",
        [
            (400, {'stage_execution_id': "a"}),
            (400, {'stage_execution_id': None}),
            (400, {}),
            (404, {'stage_execution_id': 1}),
        ]
    )
    def test_execute_wrong_stage_execution_id(self, f_step, p_request_data, p_response_code):
        response = self.client.post("/api/steps/1/execute/", p_request_data, format='multipart',
                                    content_type='application/json')

        assert response.status_code == p_response_code

    def test_execute_wrong_step_id(self):
        response = self.client.post("/api/steps/1/execute/", format='multipart', content_type='application/json')

        assert response.status_code == 404


@pytest.mark.django_db
@patch('cryton_core.lib.util.logger.logger', logger.structlog.getLogger('cryton-core-test'))
class TestWorkerViews:
    path = "cryton_core.cryton_app.views.worker_views"
    client = Client()

    @pytest.fixture
    def f_worker_model(self):
        return baker.make(WorkerModel)

    @pytest.fixture
    def f_worker(self, mocker) -> Mock:
        return mocker.patch(self.path + ".Worker")

    @pytest.mark.parametrize(
        "p_response_code, p_create_worker_effect",
        [
            (201, [1, 1]),
            (400, core_exceptions.WrongParameterError),
        ]
    )
    def test_create(self, mocker, p_response_code, p_create_worker_effect):
        data = {"name": "test", "description": "test", "force": False}

        mock_create_worker: Mock = mocker.patch(self.path + ".creator.create_worker")
        mock_create_worker.side_effect = p_create_worker_effect

        response = self.client.post(f"/api/workers/", data, content_type='application/json')

        assert response.status_code == p_response_code

    def test_healthcheck(self, f_worker):
        response = self.client.post(f"/api/workers/{1}/healthcheck/")

        assert response.status_code == 200

    def test_healthcheck_nonexistent(self, f_worker):
        f_worker.side_effect = core_exceptions.WorkerObjectDoesNotExist(1)

        response = self.client.post(f"/api/workers/{1}/healthcheck/")

        assert response.status_code == 404

    def test_destroy(self, f_worker):
        response = self.client.delete(f"/api/workers/{1}/")

        assert response.status_code == 204
        assert response.data is None

    def test_destroy_not_found(self, f_worker):
        f_worker.side_effect = core_exceptions.WorkerObjectDoesNotExist(1)

        response = self.client.delete(f"/api/workers/{1}/")

        assert response.status_code == 404

    def test_list(self, f_worker_model):
        response = self.client.get(f"/api/workers/")

        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_with_limit(self, f_worker_model):
        response = self.client.get(f"/api/workers/", {'limit': 10})

        assert response.status_code == 200
        assert response.data.get("count") == 1

    def test_retrieve(self, f_worker_model):
        response = self.client.get(f"/api/workers/{f_worker_model.id}/")

        assert response.status_code == 200
        assert response.data.get("id") == f_worker_model.id


@pytest.mark.django_db
@patch('cryton_core.lib.util.logger.logger', logger.structlog.getLogger('cryton-core-test'))
class TestQuerysetFilter:
    path = "cryton_core.cryton_app.util"
    client = Client()

    @pytest.fixture
    def f_step_models(self):
        return baker.make(StepModel, name="step1"), baker.make(StepModel, name="step2")

    @pytest.mark.parametrize(
        "p_filter, p_num_of_results",
        [
            ({}, 2),
            ({"id": -1}, 0),
            ({"name": "step"}, 2),
            ({"name": "step1"}, 1),
            ({"stage_model_id": -1}, 0),
        ]
    )
    def test_filtering(self, f_step_models, p_filter, p_num_of_results):
        p_filter.update({'limit': 10})

        response = self.client.get("/api/steps/", p_filter, content_type="application/json")

        assert p_num_of_results == len(response.data.get('results'))

    def test_ordering(self, f_step_models):
        response = self.client.get("/api/steps/", {'order_by': '-id', 'limit': 10}, content_type="application/json")

        assert response.data.get('results')[0].get('id') > response.data.get('results')[1].get('id')

    @pytest.mark.parametrize(
        "p_offset, p_num_of_results",
        [
            (0, 2),
            (1, 1),
            (2, 0),
        ]
    )
    def test_offset(self, f_step_models, p_offset, p_num_of_results):
        response = self.client.get("/api/steps/", {'offset': p_offset, 'limit': 10}, content_type="application/json")

        assert p_num_of_results == len(response.data.get('results'))

    @pytest.mark.parametrize(
        "p_limit, p_num_of_results",
        [
            (1, 1),
            (2, 2),
            (3, 2),
        ]
    )
    def test_limit(self, f_step_models, p_limit, p_num_of_results):
        response = self.client.get("/api/steps/", {'limit': p_limit}, content_type="application/json")

        assert p_num_of_results == len(response.data.get('results'))


@pytest.mark.django_db
@patch('cryton_core.lib.util.logger.logger', logger.structlog.getLogger('cryton-core-test'))
class TestUtil:
    path = "cryton_core.cryton_app.util"

    @pytest.fixture
    def f_fill_template(self, mocker) -> Mock:
        mock_fill_template: Mock = mocker.patch(self.path + ".fill_template")
        return mock_fill_template

    @pytest.fixture
    def f_get_inventory_variables_from_files(self, mocker) -> Mock:
        mock_fill_template: Mock = mocker.patch(self.path + ".get_inventory_variables_from_files")
        return mock_fill_template

    @pytest.fixture
    def f_yaml_safe_load(self, mocker) -> Mock:
        mock_safe_load: Mock = mocker.patch("yaml.safe_load")
        return mock_safe_load

    @pytest.fixture
    def f_parse_inventory(self, mocker: MockerFixture):
        return mocker.patch(self.path + ".parse_inventory")

    @pytest.mark.parametrize(
        "p_request_data",
        [
            {"start_time": "2020-10-10T10:10:10Z", "time_zone": "utc"},
            {"start_time": "2020-10-10T10:10:10.1Z", "time_zone": "utc"},
        ]
    )
    def test_get_start_time(self, mocker, p_request_data):
        mocker.patch(self.path + ".core_util.convert_to_utc", Mock(return_value=datetime(2020, 10, 10, 10, 10, 10)))

        result = util.get_start_time(p_request_data)

        assert result == datetime(2020, 10, 10, 10, 10, 10)

    @pytest.mark.parametrize(
        "p_request_data",
        [
            {"time_zone": "utc"},
            {"start_time": "2020-10-10T", "time_zone": "utc"},
            {"start_time": "2020-10-10T10:10:10Z", "time_zone": "wrong"},
        ]
    )
    def test_get_start_time_error(self, mocker, p_request_data):
        mocker.patch(self.path + ".core_util.convert_to_utc", Mock(side_effect=pytz.UnknownTimeZoneError))

        with pytest.raises(exceptions.ValidationError):
            util.get_start_time(p_request_data)

    def test_get_inventory_variables_from_files(self, f_parse_inventory):
        mock_file_content = Mock(spec=bytes)
        mock_file = Mock()
        mock_file.read.return_value = mock_file_content
        files = MultiValueDict({"file": [mock_file]})

        f_parse_inventory.return_value = {}

        result = util.get_inventory_variables_from_files(files)

        assert result == {}
        mock_file_content.decode.assert_called_once_with("utf-8")

    def test_get_inventory_variables_from_files_value_error(self, f_parse_inventory):
        files = MultiValueDict({"file": [Mock()]})

        f_parse_inventory.side_effect = ValueError

        with pytest.raises(exceptions.ValidationError):
            util.get_inventory_variables_from_files(files)

    def test_ignore_nested_undefined_getattr(self):
        res = util.IgnoreNestedUndefined(name="a")
        res = res.__getattr__("b")
        assert res.__str__() == '{{ a.b }}'

    def test_ignore_nested_undefined_getitem(self):
        res = util.IgnoreNestedUndefined(name="a")
        res = res.__getitem__("0")
        assert res.__str__() == '{{ a[0] }}'

    @pytest.mark.parametrize(
        "p_file_data, p_parsed_data",
        [
            ("test: configuration", {"test": "configuration"}),
            ("{\"test\": \"configuration\"}", {"test": "configuration"}),
            ("[SECTION]\ntest: configuration", {"SECTION": {"test": "configuration"}}),
        ]
    )
    def test_read_config(self, p_file_data, p_parsed_data):

        result = util.parse_inventory(p_file_data)

        assert result == p_parsed_data

    def test_read_config_error(self):
        with pytest.raises(ValueError):
            util.parse_inventory(": :")

    def test_fill_template(self):
        with open(TESTS_DIR + '/plan-template.yaml') as plan_yaml:
            plan_template = plan_yaml.read()
        with open(TESTS_DIR + '/inventory.yaml') as inventory:
            plan_inventory = yaml.safe_load(inventory)

        filled = util.fill_template(plan_inventory, plan_template)

        assert isinstance(filled, str)

    def test_fill_template_no_inventory_variables(self, mocker: MockerFixture):
        mock_env = mocker.patch(self.path + ".nativetypes.NativeEnvironment")
        mock_env.return_value.from_string.return_value.render.side_effect = exceptions.ValidationError("")

        with pytest.raises(exceptions.ValidationError):
            util.fill_template({"test": "test"}, "")

    def test_parse_object_from_files(self, f_get_inventory_variables_from_files, f_fill_template, f_yaml_safe_load):
        files = MultiValueDict({"file": [Mock()]})
        yaml_parser_result = {"test": "test"}

        f_get_inventory_variables_from_files.return_value = {}
        f_fill_template.return_value = ""
        f_yaml_safe_load.return_value = {"test": "test"}

        result = util.parse_object_from_files(files)

        assert result == yaml_parser_result

    @pytest.mark.parametrize(
        "p_yaml_load_error",
        [
            ValueError,
            yaml.YAMLError
        ]
    )
    def test_parse_object_from_files_wrong_template(self, f_get_inventory_variables_from_files, f_fill_template,
                                                    f_yaml_safe_load, p_yaml_load_error):
        files = MultiValueDict({"file": [Mock()]})

        f_get_inventory_variables_from_files.return_value = {}
        f_fill_template.return_value = ""
        f_yaml_safe_load.side_effect = p_yaml_load_error

        with pytest.raises(exceptions.ValidationError):
            util.parse_object_from_files(files)

    def test_parse_object_from_files_wrong_file(self):
        files = MultiValueDict({"file": Mock()})

        with pytest.raises(exceptions.ValidationError):
            util.parse_object_from_files(files)

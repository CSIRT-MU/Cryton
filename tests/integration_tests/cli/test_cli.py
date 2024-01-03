import pytest
from pytest_mock import MockerFixture
from unittest.mock import mock_open, Mock
from click.testing import CliRunner

import requests
import random
import string
import os
import yaml

from cryton_cli.lib.cli import cli


def get_random_name():
    tail = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=7))
    return '/tmp/cryton_test_file{}'.format(tail)


class TestCli:
    path_cli = 'cryton_cli.lib.cli'
    path_cmd_execution_variable = 'cryton_cli.lib.commands.execution_variable'
    path_cmd_log = 'cryton_cli.lib.commands.log'
    path_cmd_plan = 'cryton_cli.lib.commands.plan'
    path_cmd_plan_template = 'cryton_cli.lib.commands.plan_template'
    path_cmd_run = 'cryton_cli.lib.commands.run'
    path_cmd_stage = 'cryton_cli.lib.commands.stage'
    path_cmd_step = 'cryton_cli.lib.commands.step'
    path_cmd_worker = 'cryton_cli.lib.commands.worker'
    path_util = 'cryton_cli.lib.util'
    runner = CliRunner()
    response = requests.Response()
    response.status_code = 200
    response._content = b'{"results": {"id": 10}}'

    @pytest.fixture(autouse=True)
    def f_get_request(self, mocker) -> Mock:
        return mocker.patch(self.path_util + '.api.get_request', return_value=self.response)

    @pytest.fixture(autouse=True)
    def f_post_request(self, mocker) -> Mock:
        return mocker.patch(self.path_util + '.api.post_request', return_value=self.response)

    @pytest.fixture(autouse=True)
    def f_delete_request(self, mocker) -> Mock:
        return mocker.patch(self.path_util + '.api.delete_request', return_value=self.response)

    def test_cli(self):
        result = self.runner.invoke(cli)

        assert 0 == result.exit_code

    @pytest.mark.parametrize(
        "p_mock_open",
        [
            mock_open(),
            Mock(side_effect=IOError)
        ]
    )
    def test_generate_docs(self, mocker, p_mock_open):
        mocker.patch(self.path_cli + '.util.clean_up_documentation')
        mocker.patch('builtins.open', p_mock_open)

        result = self.runner.invoke(cli, ['generate-docs', 'path/to/file'])

        assert 0 == result.exit_code

    def test_runs(self):
        result = self.runner.invoke(cli, ['runs'])

        assert 0 == result.exit_code

    def test_runs_list(self):
        result = self.runner.invoke(cli, ['runs', 'list'])

        assert 0 == result.exit_code

    def test_runs_create(self):
        result = self.runner.invoke(cli, ['runs', 'create', '1', '1'])

        assert 0 == result.exit_code

    def test_runs_read(self):
        result = self.runner.invoke(cli, ['runs', 'show', '1'])

        assert 0 == result.exit_code

    def test_runs_delete(self):
        result = self.runner.invoke(cli, ['runs', 'delete', '1'])

        assert 0 == result.exit_code

    def test_runs_execute(self):
        result = self.runner.invoke(cli, ['runs', 'execute', '1'])

        assert 0 == result.exit_code

    def test_runs_execute_error(self, mocker: MockerFixture):
        mock_health_check_workers = mocker.patch("cryton_cli.lib.commands.run.run_health_check_workers")
        mock_health_check_workers.return_value = False

        result = self.runner.invoke(cli, ['runs', 'execute', '1'])

        assert 0 == result.exit_code

    def test_runs_pause(self):
        result = self.runner.invoke(cli, ['runs', 'pause', '1'])

        assert 0 == result.exit_code

    def test_runs_postpone(self):
        result = self.runner.invoke(cli, ['runs', 'postpone', '1', '00:00:00'])

        assert 0 == result.exit_code

    def test_runs_report(self):
        result = self.runner.invoke(cli, ['runs', 'report', '1'])

        assert 0 == result.exit_code

    def test_runs_reschedule(self):
        result = self.runner.invoke(cli, ['runs', 'reschedule', '1', '2020-1-1', '20:20:20'])

        assert 0 == result.exit_code

    def test_runs_reschedule_utc(self):
        result = self.runner.invoke(cli, ['runs', 'reschedule', '1', '2020-1-1', '20:20:20', '--utc-timezone'])

        assert 0 == result.exit_code

    def test_runs_schedule(self):
        result = self.runner.invoke(cli, ['runs', 'schedule', '1', '2020-1-1', '20:20:20'])

        assert 0 == result.exit_code

    def test_runs_schedule_utc(self):
        result = self.runner.invoke(cli, ['runs', 'schedule', '1', '2020-1-1', '20:20:20', '--utc-timezone'])

        assert 0 == result.exit_code

    def test_runs_unpause(self):
        result = self.runner.invoke(cli, ['runs', 'resume', '1'])

        assert 0 == result.exit_code

    def test_runs_unschedule(self):
        result = self.runner.invoke(cli, ['runs', 'unschedule', '1'])

        assert 0 == result.exit_code

    def test_runs_kill(self):
        result = self.runner.invoke(cli, ['runs', 'kill', '1'])

        assert 0 == result.exit_code

    def test_run_health_check_workers(self):
        result = self.runner.invoke(cli, ['runs', 'health-check-workers', '1'])

        assert 0 == result.exit_code

    def test_runs_validate_modules(self):
        result = self.runner.invoke(cli, ['runs', 'validate-modules', '1'])

        assert 0 == result.exit_code

    def test_runs_get_plan(self):
        result = self.runner.invoke(cli, ['runs', 'get-plan', '1'])

        assert 0 == result.exit_code

    def test_plan_templates(self):
        result = self.runner.invoke(cli, ['plan-templates'])

        assert 0 == result.exit_code

    def test_plan_templates_list(self):
        result = self.runner.invoke(cli, ['plan-templates', 'list'])

        assert 0 == result.exit_code

    def test_plan_templates_create(self):
        file = get_random_name()
        with open(file, 'w') as f:
            yaml.dump({"plan": "plan"}, f)

        result = self.runner.invoke(cli, ['plan-templates', 'create', file])

        assert 0 == result.exit_code

        os.remove(file)

    def test_plan_templates_read(self):
        result = self.runner.invoke(cli, ['plan-templates', 'show', '1'])

        assert 0 == result.exit_code

    def test_plan_templates_delete(self):
        result = self.runner.invoke(cli, ['plan-templates', 'delete', '1'])

        assert 0 == result.exit_code

    def test_plan_templates_get_template(self):
        result = self.runner.invoke(cli, ['plan-templates', 'get-template', '1'])

        assert 0 == result.exit_code

    def test_execution_variables(self):
        result = self.runner.invoke(cli, ['execution-variables'])

        assert 0 == result.exit_code

    def test_execution_variables_list(self):
        result = self.runner.invoke(cli, ['execution-variables', 'list', '-p', '1'])

        assert 0 == result.exit_code

    def test_execution_variables_create(self):
        file = get_random_name()
        with open(file, 'w') as f:
            yaml.dump({"plan": "plan"}, f)

        result = self.runner.invoke(cli, ['execution-variables', 'create', '1', file])

        assert 0 == result.exit_code

    def test_execution_variables_read(self):
        result = self.runner.invoke(cli, ['execution-variables', 'show', '1'])

        assert 0 == result.exit_code

    def test_execution_variables_delete(self):
        result = self.runner.invoke(cli, ['execution-variables', 'delete', '1'])

        assert 0 == result.exit_code

    def test_plans(self):
        result = self.runner.invoke(cli, ['plans'])

        assert 0 == result.exit_code

    def test_plans_list(self):
        result = self.runner.invoke(cli, ['plans', 'list'])

        assert 0 == result.exit_code

    def test_plans_create(self):
        result = self.runner.invoke(cli, ['plans', 'create', '1'])

        assert 0 == result.exit_code

    def test_plans_create_file_option(self):
        inv_file = get_random_name()
        with open(inv_file, 'w') as f:
            f.write('')

        result = self.runner.invoke(cli, ['plans', 'create', '1', '-i', inv_file])

        assert 0 == result.exit_code

        os.remove(inv_file)

    def test_plans_read(self):
        result = self.runner.invoke(cli, ['plans', 'show', '1'])

        assert 0 == result.exit_code

    def test_plans_delete(self):
        result = self.runner.invoke(cli, ['plans', 'delete', '1'])

        assert 0 == result.exit_code

    def test_plans_execute(self):
        result = self.runner.invoke(cli, ['plans', 'execute', '1', '1', '1'])

        assert 0 == result.exit_code

    def test_plans_validate(self):
        file = get_random_name()
        with open(file, 'w') as f:
            yaml.dump({"plan": "plan"}, f)

        result = self.runner.invoke(cli, ['plans', 'validate', file, '-i', file])

        assert 0 == result.exit_code

        os.remove(file)

    def test_plans_get_plan(self):
        result = self.runner.invoke(cli, ['plans', 'get-plan', '1'])

        assert 0 == result.exit_code

    def test_plan_executions(self):
        result = self.runner.invoke(cli, ['plan-executions'])

        assert 0 == result.exit_code

    def test_plan_executions_list(self):
        result = self.runner.invoke(cli, ['plan-executions', 'list', '-p', '1'])

        assert 0 == result.exit_code

    def test_plan_executions_delete(self):
        result = self.runner.invoke(cli, ['plan-executions', 'delete', '1'])

        assert 0 == result.exit_code

    def test_plan_executions_read(self):
        result = self.runner.invoke(cli, ['plan-executions', 'show', '1'])

        assert 0 == result.exit_code

    def test_plan_executions_pause(self):
        result = self.runner.invoke(cli, ['plan-executions', 'pause', '1'])

        assert 0 == result.exit_code

    def test_plan_executions_report(self):
        result = self.runner.invoke(cli, ['plan-executions', 'report', '1'])

        assert 0 == result.exit_code

    def test_plan_executions_unpause(self):
        result = self.runner.invoke(cli, ['plan-executions', 'resume', '1'])

        assert 0 == result.exit_code

    def test_plan_executions_validate_modules(self):
        result = self.runner.invoke(cli, ['plan-executions', 'validate-modules', '1'])

        assert 0 == result.exit_code

    def test_plan_executions_kill(self):
        result = self.runner.invoke(cli, ['plan-executions', 'kill', '1'])

        assert 0 == result.exit_code

    def test_stages(self):
        result = self.runner.invoke(cli, ['stages'])

        assert 0 == result.exit_code

    def test_stages_list(self):
        result = self.runner.invoke(cli, ['stages', 'list', '-p', '1'])

        assert 0 == result.exit_code

    def test_stages_create(self):
        file = get_random_name()
        with open(file, 'w') as f:
            yaml.dump({"stage": "stage"}, f)

        result = self.runner.invoke(cli, ['stages', 'create', '1', file])

        assert 0 == result.exit_code

        os.remove(file)

    def test_stages_read(self):
        result = self.runner.invoke(cli, ['stages', 'show', '1'])

        assert 0 == result.exit_code

    def test_stages_delete(self):
        result = self.runner.invoke(cli, ['stages', 'delete', '1'])

        assert 0 == result.exit_code

    def test_stages_validate(self):
        file = get_random_name()
        with open(file, 'w') as f:
            yaml.dump({"stage": "stage"}, f)

        result = self.runner.invoke(cli, ['stages', 'validate', file, '-i', file])

        assert 0 == result.exit_code

        os.remove(file)

    def test_stages_start_trigger(self):
        result = self.runner.invoke(cli, ['stages', 'start-trigger', '1', '1'])

        assert 0 == result.exit_code

    def test_stage_executions(self):
        result = self.runner.invoke(cli, ['stage-executions'])

        assert 0 == result.exit_code

    def test_stage_executions_list(self):
        result = self.runner.invoke(cli, ['stage-executions', 'list', '-p', '1'])

        assert 0 == result.exit_code

    def test_stage_executions_delete(self):
        result = self.runner.invoke(cli, ['stage-executions', 'delete', '1'])

        assert 0 == result.exit_code

    def test_stage_executions_read(self):
        result = self.runner.invoke(cli, ['stage-executions', 'show', '1'])

        assert 0 == result.exit_code

    def test_stage_executions_report(self):
        result = self.runner.invoke(cli, ['stage-executions', 'report', '1'])

        assert 0 == result.exit_code

    def test_stage_executions_kill(self):
        result = self.runner.invoke(cli, ['stage-executions', 'kill', '1'])

        assert 0 == result.exit_code

    def test_stage_executions_re_execute(self):
        result = self.runner.invoke(cli, ['stage-executions', 're-execute', '1'])

        assert 0 == result.exit_code

    def test_steps(self):
        result = self.runner.invoke(cli, ['steps'])

        assert 0 == result.exit_code

    def test_steps_list(self):
        result = self.runner.invoke(cli, ['steps', 'list', '-p', '1'])

        assert 0 == result.exit_code

    def test_steps_create(self):
        file = get_random_name()
        with open(file, 'w') as f:
            yaml.dump({"step": "step"}, f)

        result = self.runner.invoke(cli, ['steps', 'create', '1', file])

        assert 0 == result.exit_code

        os.remove(file)

    def test_steps_read(self):
        result = self.runner.invoke(cli, ['steps', 'show', '1'])

        assert 0 == result.exit_code

    def test_steps_delete(self):
        result = self.runner.invoke(cli, ['steps', 'delete', '1'])

        assert 0 == result.exit_code

    def test_steps_validate(self):
        file = get_random_name()
        with open(file, 'w') as f:
            yaml.dump({"step": "step"}, f)

        result = self.runner.invoke(cli, ['steps', 'validate', file, '-i', file])

        assert 0 == result.exit_code

        os.remove(file)

    def test_steps_execute(self):
        result = self.runner.invoke(cli, ['steps', 'execute', '1', '1'])

        assert 0 == result.exit_code

    def test_step_executions(self):
        result = self.runner.invoke(cli, ['step-executions'])

        assert 0 == result.exit_code

    def test_step_executions_list(self):
        result = self.runner.invoke(cli, ['step-executions', 'list', '-p', '1'])

        assert 0 == result.exit_code

    def test_step_executions_delete(self):
        result = self.runner.invoke(cli, ['step-executions', 'delete', '1'])

        assert 0 == result.exit_code

    def test_step_executions_read(self):
        result = self.runner.invoke(cli, ['step-executions', 'show', '1'])

        assert 0 == result.exit_code

    def test_step_executions_report(self):
        result = self.runner.invoke(cli, ['step-executions', 'report', '1'])

        assert 0 == result.exit_code

    def test_step_executions_kill(self):
        result = self.runner.invoke(cli, ['step-executions', 'kill', '1'])

        assert 0 == result.exit_code

    def test_step_executions_re_execute(self):
        result = self.runner.invoke(cli, ['step-executions', 're-execute', '1'])

        assert 0 == result.exit_code

    def test_workers(self):
        result = self.runner.invoke(cli, ['workers'])

        assert 0 == result.exit_code

    def test_workers_list(self):
        result = self.runner.invoke(cli, ['workers', 'list'])

        assert 0 == result.exit_code

    def test_workers_create(self):
        result = self.runner.invoke(cli, ['workers', 'create', 'name', '-d', 'name'])

        assert 0 == result.exit_code

    def test_workers_read(self):
        result = self.runner.invoke(cli, ['workers', 'show', '1'])

        assert 0 == result.exit_code

    def test_workers_delete(self):
        result = self.runner.invoke(cli, ['workers', 'delete', '1'])

        assert 0 == result.exit_code

    def test_workers_health_check(self):
        result = self.runner.invoke(cli, ['workers', 'health-check', '1'])

        assert 0 == result.exit_code

    def test_logs_list(self):
        result = self.runner.invoke(cli, ['logs', 'list', '-f', 'test'])

        assert 0 == result.exit_code

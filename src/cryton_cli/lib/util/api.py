import requests
from typing import Union

from cryton_cli.etc import config


# Endpoint urls
# Runs
RUN_LIST = config.API_ROOT + 'runs/'
RUN_CREATE = config.API_ROOT + 'runs/'
RUN_READ = config.API_ROOT + 'runs/{}/'
RUN_DELETE = config.API_ROOT + 'runs/{}/'
RUN_EXECUTE = config.API_ROOT + 'runs/{}/execute/'
RUN_PAUSE = config.API_ROOT + 'runs/{}/pause/'
RUN_POSTPONE = config.API_ROOT + 'runs/{}/postpone/'
RUN_REPORT = config.API_ROOT + 'runs/{}/report/'
RUN_RESCHEDULE = config.API_ROOT + 'runs/{}/reschedule/'
RUN_SCHEDULE = config.API_ROOT + 'runs/{}/schedule/'
RUN_UNPAUSE = config.API_ROOT + 'runs/{}/unpause/'
RUN_UNSCHEDULE = config.API_ROOT + 'runs/{}/unschedule/'
RUN_KILL = config.API_ROOT + 'runs/{}/kill/'
RUN_HEALTH_CHECK_WORKERS = config.API_ROOT + 'runs/{}/healthcheck_workers/'
RUN_VALIDATE_MODULES = config.API_ROOT + 'runs/{}/validate_modules/'
RUN_GET_PLAN = config.API_ROOT + 'runs/{}/get_plan/'

# Plans
PLAN_LIST = config.API_ROOT + 'plans/'
PLAN_CREATE = config.API_ROOT + 'plans/'
PLAN_VALIDATE = config.API_ROOT + 'plans/validate/'
PLAN_READ = config.API_ROOT + 'plans/{}/'
PLAN_DELETE = config.API_ROOT + 'plans/{}/'
PLAN_EXECUTE = config.API_ROOT + 'plans/{}/execute/'
PLAN_GET_PLAN = config.API_ROOT + 'plans/{}/get_plan/'

# PlanExecutions
PLAN_EXECUTION_LIST = config.API_ROOT + 'plan_executions/'
PLAN_EXECUTION_READ = config.API_ROOT + 'plan_executions/{}/'
PLAN_EXECUTION_DELETE = config.API_ROOT + 'plan_executions/{}/'
PLAN_EXECUTION_PAUSE = config.API_ROOT + 'plan_executions/{}/pause/'
PLAN_EXECUTION_REPORT = config.API_ROOT + 'plan_executions/{}/report/'
PLAN_EXECUTION_UNPAUSE = config.API_ROOT + 'plan_executions/{}/unpause/'
PLAN_EXECUTION_VALIDATE_MODULES = config.API_ROOT + 'plan_executions/{}/validate_modules/'
PLAN_EXECUTION_KILL = config.API_ROOT + 'plan_executions/{}/kill/'

# Stages
STAGE_LIST = config.API_ROOT + 'stages/'
STAGE_CREATE = config.API_ROOT + 'stages/'
STAGE_VALIDATE = config.API_ROOT + 'stages/validate/'
STAGE_READ = config.API_ROOT + 'stages/{}/'
STAGE_DELETE = config.API_ROOT + 'stages/{}/'
STAGE_START_TRIGGER = config.API_ROOT + 'stages/{}/start_trigger/'

# StageExecutions
STAGE_EXECUTION_LIST = config.API_ROOT + 'stage_executions/'
STAGE_EXECUTION_READ = config.API_ROOT + 'stage_executions/{}/'
STAGE_EXECUTION_DELETE = config.API_ROOT + 'stage_executions/{}/'
STAGE_EXECUTION_REPORT = config.API_ROOT + 'stage_executions/{}/report/'
STAGE_EXECUTION_KILL = config.API_ROOT + 'stage_executions/{}/kill/'
STAGE_EXECUTION_RE_EXECUTE = config.API_ROOT + 'stage_executions/{}/re_execute/'

# Steps
STEP_LIST = config.API_ROOT + 'steps/'
STEP_CREATE = config.API_ROOT + 'steps/'
STEP_VALIDATE = config.API_ROOT + 'steps/validate/'
STEP_READ = config.API_ROOT + 'steps/{}/'
STEP_DELETE = config.API_ROOT + 'steps/{}/'
STEP_EXECUTE = config.API_ROOT + 'steps/{}/execute/'

# StepExecutions
STEP_EXECUTION_LIST = config.API_ROOT + 'step_executions/'
STEP_EXECUTION_READ = config.API_ROOT + 'step_executions/{}/'
STEP_EXECUTION_DELETE = config.API_ROOT + 'step_executions/{}/'
STEP_EXECUTION_REPORT = config.API_ROOT + 'step_executions/{}/report/'
STEP_EXECUTION_KILL = config.API_ROOT + 'step_executions/{}/kill/'
STEP_EXECUTION_RE_EXECUTE = config.API_ROOT + 'step_executions/{}/re_execute/'

# Workers
WORKER_LIST = config.API_ROOT + 'workers/'
WORKER_CREATE = config.API_ROOT + 'workers/'
WORKER_READ = config.API_ROOT + 'workers/{}/'
WORKER_DELETE = config.API_ROOT + 'workers/{}/'
WORKER_HEALTH_CHECK = config.API_ROOT + 'workers/{}/healthcheck/'

# Templates
TEMPLATE_LIST = config.API_ROOT + 'templates/'
TEMPLATE_CREATE = config.API_ROOT + 'templates/'
TEMPLATE_READ = config.API_ROOT + 'templates/{}/'
TEMPLATE_DELETE = config.API_ROOT + 'templates/{}/'
TEMPLATE_GET_TEMPLATE = config.API_ROOT + 'templates/{}/get_template/'

# Execution variables
EXECUTION_VARIABLE_LIST = config.API_ROOT + 'execution_variables/'
EXECUTION_VARIABLE_CREATE = config.API_ROOT + 'execution_variables/'
EXECUTION_VARIABLE_READ = config.API_ROOT + 'execution_variables/{}/'
EXECUTION_VARIABLE_DELETE = config.API_ROOT + 'execution_variables/{}/'

# Logs
LOG_LIST = config.API_ROOT + 'logs/'


def create_rest_api_url(host: str, port: int, ssl: bool) -> str:
    """
    Create REST API URL
    :param host: Address of the host
    :param port: Port of the host
    :param ssl: If true, use HTTPS, else use HTTP
    :return: REST API URL
    """
    if ssl:
        url_prefix = 'https'
    else:
        url_prefix = 'http'
    return '{}://{}:{}/'.format(url_prefix, host, port)


def get_request(api_url: str, endpoint_url: str, object_id: int = None, custom_params: dict = None) \
        -> Union[str, requests.Response]:
    """
    Custom get request.
    :param api_url: API url
    :param endpoint_url: API endpoint url
    :param object_id: ID of the desired object
    :param custom_params: Optional dictionary containing custom params
    :return: API response
    """
    if object_id is not None:
        endpoint_url = endpoint_url.format(object_id)
    url = api_url + endpoint_url
    try:
        response = requests.get(url, custom_params)
    except requests.exceptions.ConnectionError:
        response = f'Unable to connect to {url}.'

    return response


def post_request(api_url: str, endpoint_url: str, object_id: int = None, custom_dict: dict = None, files: dict = None,
                 data: dict = None) -> Union[str, requests.Response]:
    """
    Custom post request.
    :param api_url: API url
    :param endpoint_url: API endpoint url
    :param object_id: ID of the desired object
    :param custom_dict: instance yaml
    :param files: files to be sent
    :param data: data to be sent
    :return: API response
    """
    if object_id is not None:
        endpoint_url = endpoint_url.format(object_id)
    url = api_url + endpoint_url

    try:
        response = requests.post(url, json=custom_dict, files=files, data=data)
    except requests.exceptions.ConnectionError:
        response = f'Unable to connect to {url}.'

    return response


def delete_request(api_url: str, endpoint_url: str, object_id: int = None) -> Union[str, requests.Response]:
    """
    Custom delete request.
    :param api_url: API url
    :param endpoint_url: API endpoint url
    :param object_id: ID of the desired object
    :return: API response
    """
    if object_id is not None:
        endpoint_url = endpoint_url.format(object_id)
    url = api_url + endpoint_url
    try:
        response = requests.delete(url)
    except requests.exceptions.ConnectionError:
        response = f'Unable to connect to {url}.'

    return response

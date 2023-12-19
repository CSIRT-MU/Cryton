from datetime import datetime

from cryton.hive.config.settings import SETTINGS
from cryton.hive.utility.rabbit_client import RpcClient
from cryton.hive.utility import constants

from cryton.hive.utility.logger import logger


def schedule_function(execute_function: callable, function_args: list, start_time: datetime) -> str:
    """
    Schedule a job

    :param execute_function: Function/method to be scheduled
    :param function_args: Function arguments
    :param start_time: Start time of function
    :return: ID of the scheduled job
    """
    logger.debug("Scheduling function", execute_function=str(execute_function))
    with RpcClient() as rpc:
        args = {
            'execute_function': execute_function,
            'function_args': function_args,
            'start_time': start_time.isoformat()
        }
        message = {constants.EVENT_T: constants.EVENT_UPDATE_SCHEDULER,
                   constants.EVENT_V: {constants.EVENT_ACTION: constants.ADD_JOB, "args": args}}
        logger.debug("Scheduling job", execute_function=execute_function)

        response = rpc.call(SETTINGS.rabbit.queues.control_request, message)
        logger.debug("Got response", resp=response)
        job_scheduled_id = response.get(constants.RETURN_VALUE)
        # TODO: raise error if the id is -1

    return job_scheduled_id


def schedule_repeating_function(execute_function: callable, seconds: int) -> str:
    """
    Schedule a job

    :param execute_function: Function/method to be scheduled
    :param seconds: Interval in seconds
    :return: ID of the scheduled job
    """
    logger.debug("Scheduling repeating function", execute_function=str(execute_function))
    with RpcClient() as rpc:
        args = {
            'execute_function': execute_function,
            'seconds': seconds,
        }
        message = {constants.EVENT_T: constants.EVENT_UPDATE_SCHEDULER,
                   constants.EVENT_V: {constants.EVENT_ACTION: constants.ADD_REPEATING_JOB, 'args': args}}
        response = rpc.call(SETTINGS.rabbit.queues.control_request, message)
        job_scheduled_id = response.get(constants.RETURN_VALUE)

    return job_scheduled_id


def remove_job(job_id: str) -> int:
    """
    Removes s job
    :param job_id: APS job ID
    :return: 0
    """
    logger.debug("Removing job", job_id=job_id)
    with RpcClient() as rpc:
        args = {
            'job_id': job_id
        }
        message = {constants.EVENT_T: constants.EVENT_UPDATE_SCHEDULER,
                   constants.EVENT_V: {constants.EVENT_ACTION: constants.REMOVE_JOB, 'args': args}}
        rpc.call(SETTINGS.rabbit.queues.control_request, message)

    return 0

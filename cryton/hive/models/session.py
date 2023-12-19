from typing import Union, Type

from django.core.exceptions import ObjectDoesNotExist

from cryton.hive.cryton_app.models import SessionModel, PlanExecutionModel
from cryton.hive.utility import exceptions, logger, constants, rabbit_client
from cryton.hive.models import worker


def create_session(plan_execution_id: Union[Type[int], int], session_id: str,
                   session_name: str = None) -> SessionModel:
    """

    :param plan_execution_id:
    :param session_id:
    :param session_name:
    :return:
    """
    logger.logger.debug("Creating named session", session_id=session_id, session_name=session_name)
    if not PlanExecutionModel.objects.filter(id=plan_execution_id).exists():
        raise exceptions.PlanExecutionDoesNotExist(plan_execution_id=str(plan_execution_id))

    session_object = SessionModel.objects.create(plan_execution_id=plan_execution_id,
                                                 name=session_name, msf_id=session_id)
    logger.logger.info("Named session created", session_id=session_id, session_name=session_name)

    return session_object


def get_msf_session_id(session_name: str, plan_execution_id: Union[Type[int], int]) -> str:
    """
    Get a Metasploit session ID by the defined session name

    :param str session_name: Session name provided in input file
    :param int plan_execution_id: ID of the desired plan execution
    :raises:
        SessionObjectDoesNotExist: If Session doesn't exist
    :return: Metasploit session ID
    """
    logger.logger.debug("Getting session id", session_name=session_name)
    try:
        return SessionModel.objects.get(name=session_name, plan_execution_id=plan_execution_id).msf_id
    except ObjectDoesNotExist as ex:
        raise exceptions.SessionObjectDoesNotExist(ex, session_name=session_name, plan_execution_id=plan_execution_id)


def get_session_ids(target_ip: str, plan_execution_id: Union[Type[int], int]) -> list:
    """
    Get list of session IDs to specified IP

    :param str target_ip: Target IP
    :param int plan_execution_id: ID of the desired Plan execution
    :return: List of session IDs
    """
    logger.logger.debug("Getting session ids", target_ip=target_ip)
    worker_obj = worker.Worker(worker_model_id=PlanExecutionModel.objects.get(id=plan_execution_id).worker.id)
    message = {constants.EVENT_T: constants.EVENT_LIST_SESSIONS, constants.EVENT_V: {'tunnel_peer': target_ip}}

    with rabbit_client.RpcClient() as rpc_client:
        response = rpc_client.call(worker_obj.control_q_name, message)

    return response.get(constants.EVENT_V).get('session_list')

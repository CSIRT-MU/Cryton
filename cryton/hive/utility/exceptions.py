from typing import Union, Type, List
from cryton.hive.utility import logger


class Error(Exception):
    """Base class for exceptions in this module."""


class ValidationError(Error):
    """Exception raised for errors in the validation process."""

    def __init__(self, message: Union[dict, Exception, str]):
        if type(message) != dict:
            self.message = {"message": message}
        else:
            self.message = message

        super().__init__(self.message)


class PlanValidationError(ValidationError):
    """Exception raised for errors in the Plan validation process."""

    def __init__(self, message: Union[Exception, str], plan_name: str = None):
        self.message = {"message": message, "plan_name": plan_name}
        super().__init__(self.message)


class DuplicateNameInPlan(PlanValidationError):
    """Exception raised when multiple instances have the same name in one Plan."""

    def __init__(self, unique_argument: str, duplicate_name: str, plan_name: str):
        self.message = f"{unique_argument} name '{duplicate_name}' is not unique in the plan"
        super().__init__(self.message, plan_name)


class StageValidationError(ValidationError):
    """Exception raised for errors in the Stage validation process."""

    def __init__(self, message: Union[Exception, str], stage_name: str = None):
        self.message = {"message": message, "stage_name": stage_name}
        logger.logger.error(message, stage_name=stage_name, state="fail")
        super().__init__(self.message)


class StepValidationError(ValidationError):
    """Exception raised for errors in the Step validation process."""

    def __init__(self, message: Union[Exception, str], step_name: str = None):
        self.message = {"message": message, "step_name": step_name}
        super().__init__(self.message)


class UserInputError(Error):
    """Exception raised for errors when user inputs an invalid input."""

    def __init__(self, message: Union[Exception, str], user_input: Union[str, int] = None):
        self.message = {"message": message, "user_input": user_input}
        super().__init__(self.message)


class ObjectDoesNotExist(Error):
    """Exception raised if trying to use an object that doesn't exist."""


class RunObjectDoesNotExist(ObjectDoesNotExist):
    """Exception raised if trying to use a Run object that doesn't exist."""

    def __init__(
        self, run_id: int = None, plan_id: int = None, stage_id: int = None, step_id: int = None, worker_id: int = None
    ):
        self.message = {
            "message": "RunModel does not exist.",
            "run_id": run_id,
            "plan_id": plan_id,
            "stage_id": stage_id,
            "step_id": step_id,
            "worker_id": worker_id,
        }
        super().__init__(self.message)


class PlanObjectDoesNotExist(ObjectDoesNotExist):
    """Exception raised if trying to use a Plan object that doesn't exist."""

    def __init__(self, plan_id: int = None):
        self.message = {"message": "Plan model does not exist.", "plan_id": plan_id}
        super().__init__(self.message)


class PlanExecutionDoesNotExist(ObjectDoesNotExist):
    """Exception raised if Execution does not exist."""

    def __init__(self, message: Union[Exception, str] = "PlanExecution not found", plan_execution_id: str = None):
        self.message = {"message": message, "plan_execution_id": plan_execution_id}
        super().__init__(self.message)


class StageObjectDoesNotExist(ObjectDoesNotExist):
    """Exception raised if trying to use a Stage object that doesn't exist."""

    def __init__(self, message: Union[Exception, str], stage_id: int = None, plan_id: int = None):
        self.message = {"message": message, "stage_id": stage_id, "plan_id": plan_id}
        super().__init__(self.message)


class StageExecutionObjectDoesNotExist(ObjectDoesNotExist):
    """Exception raised if trying to use a StageExecution object that doesn't exist."""

    def __init__(self, message: Union[Exception, str], stage_id: int = None, plan_id: int = None):
        self.message = {"message": message, "stage_id": stage_id, "plan_id": plan_id}
        super().__init__(self.message)


class StepObjectDoesNotExist(ObjectDoesNotExist):
    """Exception raised if trying to use a Step object that doesn't exist."""

    def __init__(
        self,
        message: Union[Exception, str],
        step_id: int = None,
        step_name: str = None,
        stage_id: Union[int, Type[int]] = None,
        plan_id: int = None,
    ):
        self.message = {
            "message": message,
            "step_id": step_id,
            "step_name": step_name,
            "stage_id": stage_id,
            "plan_id": plan_id,
        }
        super().__init__(self.message)


class StepExecutionObjectDoesNotExist(ObjectDoesNotExist):
    """Exception raised if trying to set invalid type of successor."""

    def __init__(self, message: Union[Exception, str] = "StepExecution not found", step_execution_id: str = None):
        self.message = {"message": message, "step_execution_id": step_execution_id}
        super().__init__(self.message)


class SuccessorObjectDoesNotExist(ObjectDoesNotExist):
    """Exception raised if trying to use a Successor object that doesn't exist."""

    def __init__(self, message: Union[Exception, str], step_id: int = None):
        self.message = {"message": message, "step_id": step_id}
        super().__init__(self.message)


class WorkerObjectDoesNotExist(ObjectDoesNotExist):
    """Exception raised if trying to use a Worker object that doesn't exist."""

    def __init__(self, worker_id: int):
        self.message = {"message": "WorkerModel does not exist.", "worker_id": worker_id}
        super().__init__(self.message)


class SessionObjectDoesNotExist(ObjectDoesNotExist):
    """Exception raised if trying to use a Session object that doesn't exist."""

    def __init__(
        self,
        message: Union[Exception, str],
        session_name: str = None,
        session_id: int = None,
        plan_execution_id: Union[Type[int], int] = None,
        step_id: int = None,
        plan_id: int = None,
        target=None,
        target_id=None,
    ):
        self.message = {
            "message": message,
            "session_name": session_name,
            "session_id": session_id,
            "plan_execution_id": plan_execution_id,
            "step_id": step_id,
            "plan_id": plan_id,
            "target": target,
            "target_id": target_id,
        }
        super().__init__(self.message)


class SessionIsNotOpen(Error):
    """Exception raised if the desired session isn't open."""

    def __init__(
        self, message: Union[Exception, str], session_name: str, plan_execution_id: Union[Type[int], int], step_id: int
    ):
        self.message = {
            "message": message,
            "session_name": session_name,
            "plan_execution_id": plan_execution_id,
            "step_id": step_id,
        }
        super().__init__(self.message)


class ArgumentsObjectDoesNotExist(ObjectDoesNotExist):
    """Exception raised if trying to use an Arguments object that doesn't exist."""

    def __init__(self, message: Union[Exception, str], step_id: int = None):
        self.message = {"message": message, "step_id": step_id}
        super().__init__(self.message)


class InvalidStateError(Error):
    """Exception raised if an invalid state is detected."""

    def __init__(self, message: Union[Exception, str], execution_id: int, state: str, allowed_states: list):
        self.message = {
            "message": message,
            "execution_id": execution_id,
            "state": state,
            "allowed_states": allowed_states,
        }
        super().__init__(self.message)


class RunInvalidStateError(InvalidStateError):
    """Exception raised if Run's invalid state is detected."""

    def __init__(self, message: Union[Exception, str], execution_id: int, state: str, allowed_states: list):
        super().__init__(message, execution_id, state, allowed_states)
        logger.logger.error(message, execution_id=execution_id, state=state, allowed_states=allowed_states)


class PlanInvalidStateError(InvalidStateError):
    """Exception raised if PlanExecution's invalid state is detected."""

    def __init__(self, message: Union[Exception, str], execution_id: int, state: str, allowed_states: list):
        super().__init__(message, execution_id, state, allowed_states)
        logger.logger.error(message, execution_id=execution_id, state=state, allowed_states=allowed_states)


class StageInvalidStateError(InvalidStateError):
    """Exception raised if StageExecution's invalid state is detected."""

    def __init__(self, message: Union[Exception, str], execution_id: int, state: str, allowed_states: list):
        super().__init__(message, execution_id, state, allowed_states)
        logger.logger.error(message, execution_id=execution_id, state=state, allowed_states=allowed_states)


class StepInvalidStateError(InvalidStateError):
    """Exception raised if StepExecution's invalid state is detected."""

    def __init__(self, message: Union[Exception, str], execution_id: int, state: str, allowed_states: list):
        super().__init__(message, execution_id, state, allowed_states)
        logger.logger.error(message, execution_id=execution_id, state=state, allowed_states=allowed_states)


class StateTransitionError(Error):
    """Exception raised if an invalid state transition is made."""

    def __init__(
        self,
        message: Union[Exception, str],
        execution_id: int,
        state_from: str,
        state_to: str,
        allowed_transitions: list,
    ):
        self.message = {
            "message": message,
            "execution_id": execution_id,
            "state_from": state_from,
            "state_to": state_to,
            "allowed_transitions": allowed_transitions,
        }
        super().__init__(self.message)


class RunStateTransitionError(StateTransitionError):
    """Raised if an invalid Run's state transition is made."""

    def __init__(
        self,
        message: Union[Exception, str],
        execution_id: int,
        state_from: str,
        state_to: str,
        allowed_transitions: list,
    ):
        super().__init__(message, execution_id, state_from, state_to, allowed_transitions)
        logger.logger.warning(
            "Invalid transition detected in Run", execution_id=execution_id, state_from=state_from, state_to=state_to
        )


class PlanStateTransitionError(StateTransitionError):
    """Raised if an invalid PlanExecution's state transition is made."""

    def __init__(
        self,
        message: Union[Exception, str],
        execution_id: int,
        state_from: str,
        state_to: str,
        allowed_transitions: list,
    ):
        super().__init__(message, execution_id, state_from, state_to, allowed_transitions)
        logger.logger.warning(
            "Invalid transition detected in Plan", execution_id=execution_id, state_from=state_from, state_to=state_to
        )


class StageStateTransitionError(StateTransitionError):
    """Raised if an invalid StageExecution's state transition is made."""

    def __init__(
        self,
        message: Union[Exception, str],
        execution_id: int,
        state_from: str,
        state_to: str,
        allowed_transitions: list,
    ):
        super().__init__(message, execution_id, state_from, state_to, allowed_transitions)
        logger.logger.warning(
            "Invalid transition detected in Stage", execution_id=execution_id, state_from=state_from, state_to=state_to
        )


class StepStateTransitionError(StateTransitionError):
    """Raised if an invalid StepExecution's state transition is made."""

    def __init__(
        self,
        message: Union[Exception, str],
        execution_id: int,
        state_from: str,
        state_to: str,
        allowed_transitions: list,
    ):
        super().__init__(message, execution_id, state_from, state_to, allowed_transitions)
        logger.logger.warning(
            "Invalid transition detected in Step", execution_id=execution_id, state_from=state_from, state_to=state_to
        )


class UnexpectedValue(Error):
    """Raised if an invalid value is used."""

    def __init__(self, message: Union[Exception, str], wrong_value: Union[str, int] = None):
        self.message = {"message": message, "wrong_value": wrong_value}
        super().__init__(self.message)


class MissingValueError(Error):
    """Exception raised when trying to get parameter or value that doesn't exist."""


class WrongParameterError(Error):
    """Exception raised if trying to filter in model by wrong parameter."""

    def __init__(self, message: Union[Exception, str] = "Wrong parameter name", param_name: str = None):
        self.message = {"message": message, "param_name": param_name}
        super().__init__(self.message)


class ParameterMissingError(Error):
    """Exception raised if compulsory parameter is missing."""

    def __init__(self, message: Union[Exception, str] = "Missing parameter", param_name: str = None):
        self.message = {"message": message, "param_name": param_name}
        super().__init__(self.message)


class DependencyDoesNotExist(Error):
    """Exception raised if could not create dependency between Stages."""

    def __init__(self, message: Union[Exception, str], stage_name: str = None):
        self.message = {"message": message, "stage_name": stage_name}
        logger.logger.error("stage dependency does not exist", stage_name=stage_name)
        super().__init__(self.message)


class InvalidSuccessorType(Error):
    """Exception raised if trying to set invalid type of successor."""

    def __init__(self, message: Union[Exception, str] = "Wrong successor type", successor_type: str = None):
        self.message = {"message": message, "successor_type": successor_type}
        super().__init__(self.message)


class InvalidSuccessorValue(Error):
    """Exception raised if trying to set invalid value for successor."""

    def __init__(self, message: Union[Exception, str] = "Wrong successor value", successor_value: str = None):
        self.message = {"message": message, "successor_value": successor_value}
        super().__init__(self.message)


class CreationFailedError(Error):
    """Exception raised if object creation failed."""

    def __init__(self, message: dict):
        self.message = message
        super().__init__(self.message)


class PlanCreationFailedError(CreationFailedError):
    """Exception raised if Plan creation failed."""

    def __init__(self, message: Union[Exception, str], plan_name: str = None):
        self.message = {"message": message, "plan_name": plan_name}
        logger.logger.error("plan creation failed", plan_name=plan_name)
        super().__init__(self.message)


class StageCreationFailedError(CreationFailedError):
    """Exception raised if Stage creation failed."""

    def __init__(self, message: Union[Exception, str], stage_name: str = None):
        self.message = {"message": message, "stage_name": stage_name}
        logger.logger.error("stage creation failed", stage_name=stage_name)
        super().__init__(self.message)


class StepCreationFailedError(CreationFailedError):
    """Exception raised if Step creation failed."""

    def __init__(self, message: Union[Exception, str], step_name: str = None):
        self.message = {"message": message, "step_name": step_name}
        logger.logger.error("step creation failed", step_name=step_name)
        super().__init__(self.message)


class SuccessorCreationFailedError(CreationFailedError):
    """Exception raised if Successor creation failed."""

    def __init__(self, message: Union[Exception, str], successor_name: str = None):
        self.message = {"message": message, "successor_name": successor_name}
        logger.logger.error("Successor creation failed", successor_name=successor_name)
        super().__init__(self.message)


class PlanExecutionCreationFailedError(CreationFailedError):
    """Exception raised if PlanExecution creation failed."""

    def __init__(self, message: Union[Exception, str] = "Bad argument", param_name: str = None, param_type: str = None):
        self.message = {"message": message, "param_type": param_type, "param_name": param_name}
        logger.logger.error("PlanExecution creation failed", param_name=param_name, param_type=param_type)
        super().__init__(self.message)


class RunCreationFailedError(CreationFailedError):
    """Exception raised if Run creation failed."""

    def __init__(self, message: Union[Exception, str]):
        self.message = {"message": message}
        logger.logger.error("run creation failed")
        super().__init__(self.message)


class RabbitError(Error):
    """Exception raised when there is some problem with RabbitMQ"""

    def __init__(self, message: Union[Exception, str]):
        self.message = {"message": message}
        super().__init__(self.message)


class RpcTimeoutError(RabbitError):
    """Exception raised if the RPC request timeouts"""

    def __init__(self, message: Union[Exception, str]):
        super().__init__(message)


class StageCycleDetected(Error):
    """Exception raised if there was Stage cycle detected"""

    def __init__(self, message: Union[Exception, str]):
        self.message = {"message": message}
        super().__init__(self.message)


class TriggerTypeDoesNotExist(Error):
    """Exception raised if the trigger type doesn't exist"""

    def __init__(self, trigger_type: str, supported_triggers: List):
        self.message = {
            "message": f"Nonexistent trigger type '{trigger_type}'. Supported trigger types are: "
            f"{', '.join(supported_triggers)}."
        }
        super().__init__(self.message)


class StepTypeDoesNotExist(Error):
    """Exception raised if the step type doesn't exist"""

    def __init__(self, step_type: str, supported_step_types: List):
        self.message = {
            "message": f"Nonexistent step type '{step_type}'. Supported step types are: "
            f"{', '.join(supported_step_types)}."
        }
        super().__init__(self.message)

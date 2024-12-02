from abc import ABC

from cryton.hive.utility import exceptions, logger


# States
PENDING = "PENDING"
SCHEDULED = "SCHEDULED"
STARTING = "STARTING"
RUNNING = "RUNNING"
PAUSING = "PAUSING"
PAUSED = "PAUSED"
FINISHED = "FINISHED"
IGNORED = "IGNORED"
ERROR = "ERROR"
FAILED = "FAILED"
WAITING = "WAITING"
AWAITING = "AWAITING"
STOPPED = "STOPPED"
STOPPING = "STOPPING"

UP = "UP"
DOWN = "DOWN"

# Worker related
WORKER_STATES = [UP, DOWN]

WORKER_TRANSITIONS = [(UP, DOWN), (DOWN, UP)]

# Run related
RUN_STATES = [PENDING, SCHEDULED, RUNNING, FINISHED, PAUSED, PAUSING, STOPPING, STOPPED]

RUN_TRANSITIONS = [
    (PENDING, SCHEDULED),
    (PENDING, RUNNING),
    (SCHEDULED, PENDING),
    (SCHEDULED, RUNNING),
    (RUNNING, PAUSING),
    (RUNNING, FINISHED),
    (RUNNING, STOPPING),
    (PAUSING, PAUSED),
    (PAUSING, FINISHED),
    (PAUSING, STOPPING),
    (PAUSED, RUNNING),
    (PAUSED, STOPPING),
    (STOPPING, STOPPED),
]

RUN_PREPARE_STATES = [PENDING]
RUN_SCHEDULE_STATES = [PENDING]
RUN_UNSCHEDULE_STATES = [SCHEDULED]
RUN_RESCHEDULE_STATES = [SCHEDULED]
RUN_EXECUTE_STATES = [PENDING, SCHEDULED]
RUN_EXECUTE_NOW_STATES = [PENDING]
RUN_PAUSE_STATES = [RUNNING]
RUN_RESUME_STATES = [PAUSED]
RUN_STOP_STATES = [RUNNING, PAUSING, PAUSED]
RUN_FINAL_STATES = [FINISHED, STOPPED]

RUN_PLAN_PAUSE_STATES = [PENDING, PAUSED, FINISHED, STOPPED]

# PlanExecution related
PLAN_STATES = RUN_STATES

PLAN_TRANSITIONS = RUN_TRANSITIONS

PLAN_SCHEDULE_STATES = [PENDING]
PLAN_EXECUTE_STATES = [PENDING]
PLAN_UNSCHEDULE_STATES = [SCHEDULED]
PLAN_RESCHEDULE_STATES = [SCHEDULED]
PLAN_PAUSE_STATES = [RUNNING]
PLAN_RESUME_STATES = [PAUSED]
PLAN_STOP_STATES = [RUNNING, PAUSING, PAUSED]
PLAN_FINAL_STATES = [FINISHED, STOPPED]

PLAN_STAGE_PAUSE_STATES = [PENDING, PAUSED, FINISHED, STOPPED, WAITING, AWAITING]
PLAN_RUN_EXECUTE_STATES = [RUNNING, FINISHED]

# StageExecution related
STAGE_STATES = [
    PENDING,
    SCHEDULED,
    STARTING,
    RUNNING,
    FINISHED,
    PAUSING,
    PAUSED,
    WAITING,
    AWAITING,
    STOPPING,
    STOPPED,
    ERROR,
]

STAGE_TRANSITIONS = [
    (PENDING, STARTING),
    (STARTING, AWAITING),
    (STARTING, ERROR),
    (AWAITING, PENDING),
    (AWAITING, WAITING),
    (AWAITING, RUNNING),
    (AWAITING, PAUSED),
    (AWAITING, STOPPING),
    (RUNNING, FINISHED),
    (RUNNING, PAUSING),
    (RUNNING, STOPPING),
    (PAUSING, FINISHED),
    (PAUSING, PAUSED),
    (PAUSING, STOPPING),
    (PAUSED, RUNNING),
    (PAUSED, STOPPING),
    (WAITING, RUNNING),
    (WAITING, PAUSED),
    (WAITING, STOPPING),
    (STOPPING, STOPPED),
]

STAGE_EXECUTE_STATES = [PENDING, PAUSED, WAITING, AWAITING]
STAGE_PAUSE_STATES = [RUNNING, AWAITING, WAITING]
STAGE_RESUME_STATES = [PAUSED]
STAGE_STOP_STATES = [RUNNING, PAUSING, PAUSED, WAITING, AWAITING]
STAGE_FINAL_STATES = [FINISHED, STOPPED, ERROR]

STAGE_PLAN_EXECUTE_STATES = [RUNNING, FINISHED]

# StepExecution related
STEP_STATES = [PENDING, STARTING, RUNNING, FINISHED, IGNORED, PAUSED, ERROR, STOPPING, STOPPED, FAILED]

STEP_TRANSITIONS = [
    (PENDING, STARTING),
    (PENDING, IGNORED),
    (PENDING, PAUSED),
    (STARTING, RUNNING),
    (STARTING, ERROR),
    (RUNNING, FINISHED),
    (RUNNING, FAILED),
    (RUNNING, ERROR),
    (RUNNING, STOPPING),
    (PAUSED, STARTING),
    (PAUSED, STOPPING),
    (STOPPING, STOPPED),
]

STEP_EXECUTE_STATES = [PENDING, PAUSED]
STEP_STOP_STATES = [RUNNING, PAUSED]
STEP_FINAL_STATES = [FINISHED, IGNORED, STOPPED, ERROR, FAILED]

STEP_STAGE_EXECUTE_STATES = [RUNNING, FINISHED]


class StateMachine(ABC):
    VALID_STATES: list[str]
    VALID_TRANSITIONS: list[tuple[str, str]]

    @classmethod
    def validate_transition(cls, state_from: str, state_to: str) -> bool:
        """
        Check if the transition is valid.
        :param state_from: From what state will be the transition made
        :param state_to: To what state will be the transition made
        :raises:
            InvalidStateError
            StateTransitionError
        :return: True if the transition is valid
        """
        logger.logger.debug("Checking state transition validity", state_from=state_from, state_to=state_to)
        if state_from not in cls.VALID_STATES:
            raise exceptions.InvalidStateError(f"Invalid state {state_from}! Valid states: {cls.VALID_STATES}")
        if state_to not in cls.VALID_STATES:
            raise exceptions.InvalidStateError(f"Invalid state {state_to}! Valid states: {cls.VALID_STATES}")
        if (state_from, state_to) not in cls.VALID_TRANSITIONS:
            raise exceptions.StateTransitionError(
                f"Invalid state transition from {state_from} to {state_to}! Valid transitions: {cls.VALID_TRANSITIONS}"
            )

        return True

    @staticmethod
    def validate_state(state: str, valid_states: list[str]) -> None:
        """
        Check if the state is in valid states.
        :param state: State
        :param valid_states: Valid states
        :raises:
            InvalidStateError
        :return: True if the state is in valid states
        """
        if state not in valid_states:
            raise exceptions.InvalidStateError(f"State {state} is not in {valid_states}.")


class RunStateMachine(StateMachine):
    VALID_STATES = RUN_STATES
    VALID_TRANSITIONS = RUN_TRANSITIONS


class PlanStateMachine(StateMachine):
    VALID_STATES = PLAN_STATES
    VALID_TRANSITIONS = PLAN_TRANSITIONS


class StageStateMachine(StateMachine):
    VALID_STATES = STAGE_STATES
    VALID_TRANSITIONS = STAGE_TRANSITIONS


class StepStateMachine(StateMachine):
    VALID_STATES = STEP_STATES
    VALID_TRANSITIONS = STEP_TRANSITIONS

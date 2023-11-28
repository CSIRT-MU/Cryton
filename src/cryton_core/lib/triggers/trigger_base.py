from datetime import datetime
from django.utils import timezone
import schema

from cryton_core.lib.models import stage, worker, step
from cryton_core.lib.util.rabbit_client import RpcClient
from cryton_core.lib.util import constants, exceptions, logger, scheduler_client, states


class TriggerBase:
    arg_schema = schema.Schema({})

    def __init__(self, stage_execution):  # Not using typing since it's causing loop import error
        """
        :param stage_execution: StageExecution's object
        """
        self.stage_execution: stage.StageExecution = stage_execution
        self.stage_execution_id = self.stage_execution.model.id
        self.trigger_args = self.stage_execution.model.stage_model.trigger_args

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def pause(self) -> None:
        pass

    def unpause(self) -> None:
        """
        Unpause stage execution.
        :return: None
        """
        logger.logger.info("Stage execution unpausing", stage_execution_id=self.stage_execution_id)
        states.StageStateMachine(self.stage_execution.model.id).validate_state(self.stage_execution.state,
                                                                               states.STAGE_UNPAUSE_STATES)

        self.stage_execution.state = states.RUNNING
        self.stage_execution.pause_time = None

        if self.stage_execution.all_steps_finished:
            self.stage_execution.finish()
        else:
            for step_exec in self.stage_execution.model.step_executions.filter(state=states.PAUSED):
                step.StepExecutionType[step_exec.step_model.step_type].value(step_execution_id=step_exec.id).execute()


class TriggerTime(TriggerBase):
    def __init__(self, stage_execution):
        """
        :param stage_execution: StageExecution's object
        """
        super().__init__(stage_execution)

    def start(self) -> None:
        """
        Runs schedule() method.
        :return: None
        """
        self.schedule()

    def stop(self) -> None:
        """
        Runs unschedule() method.
        :return: None
        """
        self.unschedule()

    def schedule(self) -> None:
        """
        Schedule stage execution.
        :return: None
        """

        states.StageStateMachine(self.stage_execution_id).validate_state(self.stage_execution.state,
                                                                         states.STAGE_SCHEDULE_STATES)
        if self.stage_execution.model.stage_model.trigger_type not in [constants.DELTA, constants.DATETIME]:
            raise exceptions.UnexpectedValue(
                'StageExecution with ID {} cannot be scheduled due to not having delta or datetime parameter'.format(
                    self.stage_execution_id)
            )

        logger.logger.debug("Creating schedule time for Stage execution", stage_execution_id=self.stage_execution_id)
        schedule_time = self._create_schedule_time()
        self.stage_execution.schedule_time = schedule_time
        self.stage_execution.pause_time = None
        self.stage_execution.state = states.SCHEDULED
        self.stage_execution.aps_job_id = scheduler_client.schedule_function(
            "cryton_core.lib.models.stage:execution", [self.stage_execution_id], schedule_time)

        logger.logger.info("Stage execution scheduled", stage_execution_id=self.stage_execution_id,
                           stage_name=self.stage_execution.model.stage_model.name, status='success')

    def unschedule(self) -> None:
        """
        Unschedule StageExecution from a APScheduler.
        :raises:
            ConnectionRefusedError
        :return: None
        """
        logger.logger.debug("Unscheduling Stage execution", stage_execution_id=self.stage_execution_id)
        states.StageStateMachine(self.stage_execution_id).validate_state(self.stage_execution.state,
                                                                         states.STAGE_UNSCHEDULE_STATES)

        scheduler_client.remove_job(self.stage_execution.aps_job_id)
        self.stage_execution.aps_job_id, self.stage_execution.schedule_time = "", None
        self.stage_execution.state = states.PENDING

        logger.logger.info("Stage execution unscheduled", stage_execution_id=self.stage_execution_id,
                           stage_name=self.stage_execution.model.stage_model.name, status='success')

    def pause(self) -> None:
        """
        Pause stage execution.
        :return: None
        """
        if self.stage_execution.state in states.STAGE_UNSCHEDULE_STATES:
            self.unschedule()
            self.stage_execution.pause_time = timezone.now()

        # If stage is RUNNING, set PAUSING state. It will be PAUSED once the currently
        # RUNNING step finished and listener gets it's return value
        elif self.stage_execution.state == states.RUNNING:
            logger.logger.info("Stage execution pausing", stage_execution_id=self.stage_execution_id)
            self.stage_execution.state = states.PAUSING

    def _create_schedule_time(self) -> datetime:
        pass


class TriggerWorker(TriggerBase):
    def __init__(self, stage_execution):
        super().__init__(stage_execution)

    def _rpc_start(self, event_v: dict) -> None:
        """
        Start trigger's listener on worker.
        :param event_v: Special trigger parameters for listener on worker
        :return: None
        """
        logger.logger.debug("Starting Stage execution trigger", stage_execution_id=self.stage_execution_id,
                            trigger_id=self.stage_execution.trigger_id)

        worker_obj = worker.Worker(worker_model_id=self.stage_execution.model.plan_execution.worker.id)
        event_v.update(self.trigger_args)
        message = {constants.EVENT_T: constants.EVENT_ADD_TRIGGER, constants.EVENT_V: event_v}

        self.stage_execution.state = states.STARTING

        with RpcClient() as rpc:
            try:
                response = rpc.call(worker_obj.control_q_name, message)
            except exceptions.RpcTimeoutError:
                self.stage_execution.state = states.ERROR
                logger.logger.error("Couldn't start Stage Execution trigger - RPC timeout",
                                    stage_execution_id=self.stage_execution_id)
                return

        # TODO: When changing the Stage's state to final state, it must propagate to PlanEx
        #  Each execution component should have its `process_finished` method, maybe create event `process_finished`
        if response.get(constants.EVENT_V).get(constants.RETURN_CODE) == 0:
            self.stage_execution.trigger_id = response.get(constants.EVENT_V).get(constants.TRIGGER_ID)
            self.stage_execution.state = states.AWAITING
            logger.logger.info("Stage Execution trigger started.", stage_execution_id=self.stage_execution_id)
        else:
            self.stage_execution.state = states.ERROR
            logger.logger.error("Couldn't start Stage Execution trigger.", stage_execution_id=self.stage_execution_id)

    def _rpc_stop(self) -> None:
        """
        Stop trigger's listener on worker.
        :return: None
        """
        logger.logger.debug("Stopping Stage execution trigger", stage_execution_id=self.stage_execution_id,
                            trigger_id=self.stage_execution.trigger_id)
        worker_obj = worker.Worker(worker_model_id=self.stage_execution.model.plan_execution.worker.id)
        message = {constants.EVENT_T: constants.EVENT_REMOVE_TRIGGER,
                   constants.EVENT_V: {constants.TRIGGER_ID: self.stage_execution.trigger_id}}

        with RpcClient() as rpc:
            try:
                response = rpc.call(worker_obj.control_q_name, message)
            except exceptions.RpcTimeoutError:
                logger.logger.error("Couldn't start Stage Execution trigger - RPC timeout",
                                    stage_execution_id=self.stage_execution_id)
                return

        if response.get(constants.EVENT_V).get(constants.RETURN_CODE) == 0:
            logger.logger.info("Stage Execution trigger stopped.", stage_execution_id=self.stage_execution_id,
                               trigger_id=self.stage_execution.trigger_id)
            self.stage_execution.trigger_id = ""
        else:
            logger.logger.warning("Couldn't stop Stage Execution trigger.", stage_execution_id=self.stage_execution_id)

    def pause(self) -> None:
        """
        Pause stage execution.
        :return: None
        """
        # If stage is RUNNING, set PAUSING state. It will be PAUSED once the currently
        # RUNNING step finishes and listener gets its return value.
        if self.stage_execution.state == states.RUNNING:
            logger.logger.info("Stage execution pausing", stage_execution_id=self.stage_execution_id)
            self.stage_execution.state = states.PAUSING

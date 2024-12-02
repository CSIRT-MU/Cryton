from typing import Type
from datetime import datetime
from django.utils import timezone
from threading import Thread

from django.db import transaction, connections

from cryton.hive.cryton_app.models import StageModel, StageExecutionModel
from cryton.hive.utility import logger, states as st, util
from cryton.hive.triggers import (
    TriggerType,
    TriggerDelta,
    TriggerHTTP,
    TriggerMetasploit,
    TriggerTime,
    TriggerImmediate,
)
from cryton.hive.models.step import StepExecution
from cryton.hive.models.worker import Worker
from cryton.hive.config.settings import SETTINGS
from cryton.hive.models.abstract import Instance, Execution


class Stage(Instance):
    def __init__(self, model_id: int):
        """
        :param model_id: Model ID
        """
        self.__model = StageModel.objects.get(id=model_id)

    @staticmethod
    def create_model(plan_id: int, name: str, trigger_type: str, arguments: dict, metadata: dict) -> StageModel:
        return StageModel.objects.create(
            plan_id=plan_id, name=name, metadata=metadata, type=trigger_type, arguments=arguments
        )

    def delete(self):
        self.model.delete()

    @property
    def model(self) -> Type[StageModel] | StageModel:
        self.__model.refresh_from_db()
        return self.__model

    @property
    def name(self) -> str:
        return self.model.name

    @property
    def trigger_type(self) -> str:
        return self.model.type

    @property
    def meta(self) -> dict:
        return self.model.metadata


class StageExecution(Execution):
    def __init__(self, model_id: int):
        """
        :param model_id: Model ID
        """
        self.__model = StageExecutionModel.objects.get(id=model_id)

    @staticmethod
    def create_model(stage_id: int, plan_execution_id: int) -> StageExecutionModel | Type[StageExecutionModel]:
        return StageExecutionModel.objects.create(stage_id=stage_id, plan_execution_id=plan_execution_id)

    @classmethod
    def prepare(cls, stage_id: int, plan_execution_id: int) -> "StageExecution":
        model = cls.create_model(stage_id, plan_execution_id)

        for step in model.stage.steps.all():
            StepExecution.prepare(step.id, model.id)

        return StageExecution(model.id)

    def delete(self):
        self.model.delete()

    @property
    def model(self) -> Type[StageExecutionModel] | StageExecutionModel:
        self.__model.refresh_from_db()
        return self.__model

    @property
    def state(self) -> str:
        return self.model.state

    @state.setter
    def state(self, value: str):
        with transaction.atomic():
            StageExecutionModel.objects.select_for_update().get(id=self.model.id)
            if st.StageStateMachine.validate_transition(self.state, value):
                logger.logger.debug(
                    "Stage execution changed state",
                    state_from=self.state,
                    state_to=value,
                    stage_execution_id=self.model.id,
                )
                model = self.model
                model.state = value
                model.save()

    @property
    def aps_job_id(self) -> str:
        return self.model.job_id

    @aps_job_id.setter
    def aps_job_id(self, value: str):
        model = self.model
        model.job_id = value
        model.save()

    @property
    def start_time(self) -> datetime | None:
        return self.model.start_time

    @start_time.setter
    def start_time(self, value: datetime | None):
        model = self.model
        model.start_time = value
        model.save()

    @property
    def schedule_time(self) -> datetime | None:
        return self.model.schedule_time

    @schedule_time.setter
    def schedule_time(self, value: datetime | None):
        model = self.model
        model.schedule_time = value
        model.save()

    @property
    def pause_time(self) -> datetime | None:
        return self.model.pause_time

    @pause_time.setter
    def pause_time(self, value: datetime | None):
        model = self.model
        model.pause_time = value
        model.save()

    @property
    def finish_time(self) -> datetime | None:
        return self.model.finish_time

    @finish_time.setter
    def finish_time(self, value: datetime | None):
        model = self.model
        model.finish_time = value
        model.save()

    @property
    def trigger_id(self) -> str:
        return self.model.trigger_id

    @trigger_id.setter
    def trigger_id(self, value: str):
        model = self.model
        model.trigger_id = value
        model.save()

    @property
    def output(self) -> str:
        return self.model.output

    @output.setter
    def output(self, value: str):
        model = self.model
        model.output = value
        model.save()

    @property
    def serialized_output(self) -> list | dict:
        return self.model.serialized_output

    @serialized_output.setter
    def serialized_output(self, value: list | dict):
        model = self.model
        model.serialized_output = value
        model.save()

    @property
    def trigger(self) -> TriggerDelta | TriggerHTTP | TriggerMetasploit | TriggerTime | TriggerImmediate:
        return TriggerType[self.model.stage.type].value()

    @property
    def all_steps_finished(self) -> bool:
        return not self.model.step_executions.exclude(state__in=st.STEP_FINAL_STATES).exists()

    @property
    def all_dependencies_finished(self) -> bool:
        dependencies = self.model.stage.dependencies.values("dependency")
        execution_dependencies = self.model.plan_execution.stage_executions.filter(stage__in=dependencies)
        unfinished_dependencies = execution_dependencies.exclude(state=st.FINISHED)
        return not unfinished_dependencies.exists()

    @property
    def control_queue(self):
        return Worker(self.model.plan_execution.worker.id).control_queue

    @staticmethod
    def _run_step_executions(step_executions: list[StepExecution]):
        """
        Evenly distribute Step executions and run each batch in a Process.
        :param step_executions: Step executions to be distributed into Processes
        :return: None
        """
        # Evenly distribute StepExecutions into processes.
        step_exec_lists = list(util.split_into_lists(step_executions, SETTINGS.cpu_cores))
        processes = []
        for step_executions in step_exec_lists:
            if step_executions:
                processes.append(
                    logger.LoggedProcess(
                        logg_queue=logger.logger_object.log_queue,
                        target=util.run_executions_in_threads,
                        args=(step_executions,),
                    )
                )

        # Close django db connections and run processes
        connections.close_all()
        for process in processes:
            process.start()

    def start(self):
        self.state = st.STARTING

        try:
            trigger_id, schedule_time = self.trigger.start(
                arguments=self.model.stage.arguments, stage_execution_id=self.model.id, queue=self.control_queue
            )
        except Exception as ex:
            # TODO: When changing the Stage's state to final state, it must propagate to PlanEx
            #  Each execution component should have its `process_finished` method, maybe create event `process_finished`
            logger.logger.error(f"Unable to start trigger", stage_execution_id=self.model.id, error=str(ex))
            self.state = st.ERROR
            return

        if schedule_time:
            self.schedule_time = schedule_time
        if trigger_id:
            self.trigger_id = trigger_id
        self.state = st.AWAITING

        if isinstance(self.trigger, TriggerImmediate):
            Thread(target=self.execute).start()

    def stop(self):
        logger.logger.debug("stopping stage", stage_execution_id=self.model.id)
        st.StageStateMachine.validate_state(self.state, st.STAGE_STOP_STATES)

        state_before = self.state
        self.state = st.STOPPING

        if state_before == st.AWAITING:
            self.trigger.stop(trigger_id=self.trigger_id, queue=self.control_queue)
        elif state_before == st.WAITING:
            pass
        else:
            threads = list()
            for step_ex_model in self.model.step_executions.filter(state__in=st.STEP_STOP_STATES):
                step_ex = StepExecution(step_ex_model.id)
                thread = Thread(target=step_ex.stop)
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

        self.finish_time = timezone.now()
        self.state = st.STOPPED
        logger.logger.info("stage execution stopped", stage_execution_id=self.model.id)

    def execute(self) -> None:
        """
        Check if all requirements for execution are met, get init steps and execute them.
        :return: None
        """
        logger.logger.debug("Executing Stage", stage_execution_id=self.model.id)
        st.StageStateMachine.validate_state(self.state, st.STAGE_EXECUTE_STATES)

        # Stop the execution if dependencies aren't finished.
        if not self.all_dependencies_finished:
            self.state = st.WAITING
            return

        # Get initial Steps in Stage
        step_executions = []
        for step_ex_model in self.model.step_executions.filter(state=st.PENDING, step__is_init=True):
            step_executions.append(StepExecution(step_ex_model.id))

        # Pause waiting and awaiting StageExecutions if PlanExecution isn't running.
        if self.state in [st.WAITING, st.AWAITING] and self.model.plan_execution.state != st.RUNNING:
            self.pause_time = timezone.now()
            self.state = st.PAUSED
            for step_ex in step_executions:
                step_ex.state = st.PAUSED
            return

        # Update state and time
        if self.start_time is None:
            self.start_time = timezone.now()
        self.state = st.RUNNING

        self._run_step_executions(step_executions)

        logger.logger.info("stage execution executed", stage_execution_id=self.model.id)

    def pause(self):
        """
        Pause stage execution.
        :return: None
        """
        logger.logger.info("stage execution pausing", stage_execution_id=self.model.id)
        st.StageStateMachine.validate_state(self.state, st.STAGE_PAUSE_STATES)
        if self.state in [st.AWAITING]:
            try:
                self.trigger.stop(trigger_id=self.trigger_id, queue=self.control_queue)
            except Exception as ex:
                logger.logger.warning("stage execution cannot be paused", exception=str(ex))
                return
            self.pause_time = timezone.now()

        # If stage is RUNNING, set PAUSING state. It will be PAUSED by the currently RUNNING step(s)
        elif self.state == st.RUNNING:
            self.state = st.PAUSING

    def resume(self):
        logger.logger.info("stage execution resuming", stage_execution_id=self.model.id)
        st.StageStateMachine.validate_state(self.state, st.STAGE_RESUME_STATES)

        self.state = st.RUNNING
        self.pause_time = None

        if self.all_steps_finished:
            self.finish()
            return

        # TODO: pass new_start_time for the trigger
        #  self.stage_execution.model.plan_execution.start_time - self.stage_execution.pause_time
        for step_exec in self.model.step_executions.filter(state=st.PAUSED):
            StepExecution(step_exec.id).start()

    def validate_modules(self) -> None:
        """
        Check if module is present and module args are correct for each Step
        """
        logger.logger.debug("Validating stage modules", stage_execution_id=self.model.id)
        for step_ex_id in self.model.step_executions.values_list("id", flat=True):
            StepExecution(step_ex_id).validate()

    def report(self) -> dict:
        logger.logger.debug("Generating Stage report", stage_execution_id=self.model.id)
        report_obj = dict(
            id=self.model.id,
            name=self.model.stage.name,
            metadata=self.model.stage.metadata,
            state=self.state,
            schedule_time=self.schedule_time,
            start_time=self.start_time,
            finish_time=self.finish_time,
            pause_time=self.pause_time,
            step_executions=[],
        )

        for step_execution_model in self.model.step_executions.order_by("id"):
            step_execution_report = StepExecution(step_execution_model.id).report()
            report_obj["step_executions"].append(step_execution_report)

        return report_obj

    def _execute_subjects_to_dependency(self) -> None:
        """
        Execute WAITING StageExecution subjects to specified StageExecution dependency.
        :return: None
        """
        logger.logger.debug("Executing Stage dependency subjects", stage_execution_id=self.model.id)
        subject_to_ids = self.model.stage.subjects_to.all().values_list("stage_id", flat=True)
        subject_to_exs = self.model.plan_execution.stage_executions.filter(
            stage_id__in=subject_to_ids, state=st.WAITING
        )
        for subject_to_ex in subject_to_exs:
            subject_to_ex_obj = StageExecution(subject_to_ex.id)
            Thread(target=subject_to_ex_obj.execute).run()

    def re_execute(self, immediately: bool = False) -> None:
        """
        Reset execution data and re-execute StageExecution.
        :return: None
        """
        st.StageStateMachine.validate_state(self.state, st.STAGE_FINAL_STATES)
        self._reset_execution_data()
        if immediately:
            self.execute()
        else:
            self.trigger.start()

    def _reset_execution_data(self) -> None:
        """
        Reset changeable data to defaults and reset StepExecutions.
        :return: None
        """
        logger.logger.debug("Resetting Stage execution data", stage_execution_id=self.model.id)
        st.StageStateMachine.validate_state(self.state, st.STAGE_FINAL_STATES)

        with transaction.atomic():
            model = self.model
            StageExecutionModel.objects.select_for_update().get(id=model.id)

            model.state = st.PENDING
            model.job_id = ""
            model.trigger_id = ""
            model.start_time = None
            model.schedule_time = None
            model.pause_time = None
            model.finish_time = None
            model.save()

        for step_ex_model in self.model.step_executions.all():
            StepExecution(step_ex_model.id).reset_execution_data()

    def finish(self) -> None:
        """
        Finish execution - update necessary variables, execute dependencies, and stop trigger.
        :return: None
        """
        st.StageStateMachine.validate_state(self.state, [st.PAUSING, st.RUNNING])
        logger.logger.info("Stage execution finished", stage_execution_id=self.model.id)

        self.state = st.FINISHED
        self.finish_time = timezone.now()
        self._execute_subjects_to_dependency()


def execution(execution_id: int) -> None:
    """
    Create StageExecution object and call its execute method
    :param execution_id: desired StageExecution's ID
    :return: None
    """
    logger.logger.debug("Starting Stage execution", stage_execution_id=execution_id)
    StageExecution(execution_id).execute()

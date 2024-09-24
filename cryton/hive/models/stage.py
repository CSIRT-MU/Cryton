from typing import Union, Type, Optional, List
from datetime import datetime
from django.utils import timezone
from threading import Thread

from django.db.models.query import QuerySet
from django.core import exceptions as django_exc
from django.db import transaction, connections

from cryton.hive.cryton_app.models import StageModel, StageExecutionModel, StepExecutionModel, StageDependencyModel
from cryton.hive.utility import exceptions, logger, states as st, util
from cryton.hive.triggers import TriggerType, TriggerDelta, TriggerHTTP, TriggerMSF, TriggerDateTime
from cryton.hive.models.step import StepExecution, Step
from cryton.hive.config.settings import SETTINGS

from dataclasses import dataclass, asdict


@dataclass
class StageReport:
    id: int
    name: str
    metadata: dict
    state: str
    start_time: datetime
    pause_time: datetime
    finish_time: datetime
    schedule_time: datetime
    step_executions: list


class Stage:
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
    def model(self) -> Union[Type[StageModel], StageModel]:
        self.__model.refresh_from_db()
        return self.__model

    @property
    def name(self) -> str:
        return self.model.name

    @name.setter
    def name(self, value):
        model = self.model
        model.name = value
        model.save()

    @property
    def trigger_type(self) -> str:
        return self.model.type

    @trigger_type.setter
    def trigger_type(self, value: str):
        model = self.model
        model.type = value
        model.save()

    @property
    def meta(self) -> dict:
        return self.model.metadata

    @meta.setter
    def meta(self, value: dict):
        model = self.model
        model.metadata = value
        model.save()

    @property
    def final_steps(self) -> QuerySet:
        steps_list = Step.filter(stage_id=self.model.id, is_final=True)
        return steps_list

    @property
    def execution_list(self) -> QuerySet:
        """
        Returns StageExecutionModel QuerySet. If the latest is needed, use '.latest()' on result.
        :return: QuerySet of StageExecutionModel
        """
        return StageExecutionModel.objects.filter(stage_id=self.model.id)

    @staticmethod
    def filter(**kwargs) -> QuerySet:
        """
        :param kwargs: dict of parameters to filter by
        :return: QuerySet of StageModel
        """
        if kwargs:
            try:
                return StageModel.objects.filter(**kwargs)
            except django_exc.FieldError as e:
                raise exceptions.WrongParameterError(e)
        else:
            return StageModel.objects.all()

    def add_dependency(self, dependency_id: int) -> int:
        """
        Create dependency object
        :param dependency_id: Stage ID
        :return: ID of the dependency object
        """
        logger.logger.debug("Creating stage dependency", stage_id=self.model.id, dependency_id=dependency_id)
        dependency_obj = StageDependencyModel(stage_id=self.model.id, dependency_id=dependency_id)
        dependency_obj.save()
        logger.logger.debug("Stage dependency created", stage_id=self.model.id, dependency_id=dependency_id)

        return dependency_obj.id


class StageExecution:
    def __init__(self, **kwargs):
        """
        :param kwargs:
        (optional) stage_execution_id: int - for retrieving existing execution
        stage_id: int - for creating new execution
        """
        stage_execution_id = kwargs.get("stage_execution_id")
        if stage_execution_id:
            try:
                self.model = StageExecutionModel.objects.get(id=stage_execution_id)
            except django_exc.ObjectDoesNotExist:
                raise exceptions.StageExecutionObjectDoesNotExist(
                    "StageExecutionModel with id {} does not exist.".format(stage_execution_id), stage_execution_id
                )

        else:
            self.model = StageExecutionModel.objects.create(**kwargs)
            self._prepare_executions()

    def delete(self):
        self.model.delete()

    @property
    def model(self) -> Union[Type[StageExecutionModel], StageExecutionModel]:
        self.__model.refresh_from_db()
        return self.__model

    @model.setter
    def model(self, value: StageExecutionModel):
        self.__model = value

    @property
    def state(self) -> str:
        return self.model.state

    @state.setter
    def state(self, value: str):
        with transaction.atomic():
            StageExecutionModel.objects.select_for_update().get(id=self.model.id)
            if st.StageStateMachine(self.model.id).validate_transition(self.state, value):
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
    def start_time(self) -> Optional[datetime]:
        return self.model.start_time

    @start_time.setter
    def start_time(self, value: Optional[datetime]):
        model = self.model
        model.start_time = value
        model.save()

    @property
    def schedule_time(self) -> Optional[datetime]:
        return self.model.schedule_time

    @schedule_time.setter
    def schedule_time(self, value: Optional[datetime]):
        model = self.model
        model.schedule_time = value
        model.save()

    @property
    def pause_time(self) -> Optional[datetime]:
        return self.model.pause_time

    @pause_time.setter
    def pause_time(self, value: Optional[datetime]):
        model = self.model
        model.pause_time = value
        model.save()

    @property
    def finish_time(self) -> Optional[datetime]:
        return self.model.finish_time

    @finish_time.setter
    def finish_time(self, value: Optional[datetime]):
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
    def serialized_output(self) -> Union[list, dict]:
        return self.model.serialized_output

    @serialized_output.setter
    def serialized_output(self, value: Union[list, dict]):
        model = self.model
        model.serialized_output = value
        model.save()

    @property
    def trigger(self) -> Union[TriggerDelta, TriggerHTTP, TriggerMSF, TriggerDateTime]:
        trigger_type = self.model.stage.type
        return TriggerType[trigger_type].value(stage_execution=self)

    @property
    def all_steps_finished(self) -> bool:
        return not self.model.step_executions.exclude(state__in=st.STEP_FINAL_STATES).exists()

    @property
    def all_dependencies_finished(self) -> bool:
        dependency_ids = self.model.stage.dependencies.all().values_list("dependency_id", flat=True)
        cond = (
            self.filter(stage_id__in=dependency_ids, plan_execution_id=self.model.plan_execution_id)
            .exclude(state=st.FINISHED)
            .exists()
        )

        return not cond

    @staticmethod
    def filter(**kwargs) -> QuerySet:
        """
        Get list of StageExecutionModel according to no or specified conditions
        :param kwargs: dict of parameters to filter by
        :return: Desired QuerySet
        """
        if kwargs:
            try:
                return StageExecutionModel.objects.filter(**kwargs)
            except django_exc.FieldError as ex:
                raise exceptions.WrongParameterError(message=ex)
        else:
            return StageExecutionModel.objects.all()

    def _prepare_executions(self):
        """
        Prepare execution for each Step.
        :return: None
        """
        step_execution_kwargs = {"stage_execution": self.model}
        for step_obj in self.model.stage.steps.all():
            step_execution_kwargs.update({"step": step_obj})
            StepExecution(**step_execution_kwargs)

    @staticmethod
    def _run_step_executions(step_executions: List[StepExecution]):
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

    def execute(self) -> None:
        """
        Check if all requirements for execution are met, get init steps and execute them.
        :return: None
        """
        logger.logger.debug("Executing Stage", stage_execution_id=self.model.id)
        st.StageStateMachine(self.model.id).validate_state(self.state, st.STAGE_EXECUTE_STATES)

        # Stop the execution if dependencies aren't finished.
        if not self.all_dependencies_finished:
            self.state = st.WAITING
            return

        # Get initial Steps in Stage
        step_executions = []
        for step_ex_model in self.model.step_executions.filter(state=st.PENDING, step__is_init=True):
            step_executions.append(StepExecution(step_execution_id=step_ex_model.id))

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

        logger.logger.info(
            "Stage execution executed",
            stage_execution_id=self.model.id,
            stage_name=self.model.stage.name,
            status="success",
        )

    def validate_modules(self) -> None:
        """
        Check if module is present and module args are correct for each Step
        """
        logger.logger.debug("Validating stage modules", stage_execution_id=self.model.id)
        for step_ex_id in self.model.step_executions.values_list("id", flat=True):
            StepExecution(step_execution_id=step_ex_id).validate()

    def report(self) -> dict:
        logger.logger.debug("Generating Stage report", stage_execution_id=self.model.id)
        report_obj = StageReport(
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

        for step_execution_obj in StepExecutionModel.objects.filter(stage_execution_id=self.model.id).order_by("id"):
            step_ex_report = StepExecution(step_execution_id=step_execution_obj.id).report()
            report_obj.step_executions.append(step_ex_report)

        return asdict(report_obj)

    def kill(self) -> None:
        """
        Kill current StageExecution and its StepExecutions.
        :return: None
        """
        logger.logger.debug("Killing Stage", stage_execution_id=self.model.id)
        st.StageStateMachine(self.model.id).validate_state(self.state, st.STAGE_KILL_STATES)

        state_before = self.state
        self.state = st.TERMINATING

        if state_before == st.AWAITING:
            self.trigger.stop()

        elif state_before == st.WAITING:
            pass

        else:
            threads = list()

            # Kill Step executions
            for step_ex_model in self.model.step_executions.filter(state__in=st.STEP_KILL_STATES):
                step_ex = StepExecution(step_execution_id=step_ex_model.id)
                thread = Thread(target=step_ex.kill)
                threads.append(thread)

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

        self.finish_time = timezone.now()
        self.state = st.TERMINATED
        logger.logger.info(
            "Stage execution killed",
            stage_execution_id=self.model.id,
            stage_name=self.model.stage.name,
            status="success",
        )

    def execute_subjects_to_dependency(self) -> None:
        """
        Execute WAITING StageExecution subjects to specified StageExecution dependency.
        :return: None
        """
        logger.logger.debug("Executing Stage dependency subjects", stage_execution_id=self.model.id)
        subject_to_ids = self.model.stage.subjects_to.all().values_list("stage_id", flat=True)
        subject_to_exs = self.filter(
            stage_id__in=subject_to_ids, plan_execution_id=self.model.plan_execution_id, state=st.WAITING
        )
        for subject_to_ex in subject_to_exs:
            subject_to_ex_obj = StageExecution(stage_execution_id=subject_to_ex.id)
            Thread(target=subject_to_ex_obj.execute).run()

    def re_execute(self, immediately: bool = False) -> None:
        """
        Reset execution data and re-execute StageExecution.
        :return: None
        """
        st.StageStateMachine(self.model.id).validate_state(self.state, st.STAGE_FINAL_STATES)
        self.reset_execution_data()
        if immediately:
            self.execute()
        else:
            self.trigger.start()

    def reset_execution_data(self) -> None:
        """
        Reset changeable data to defaults and reset StepExecutions.
        :return: None
        """
        logger.logger.debug("Resetting Stage execution data", stage_execution_id=self.model.id)
        st.StageStateMachine(self.model.id).validate_state(self.state, st.STAGE_FINAL_STATES)

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
            StepExecution(step_execution_id=step_ex_model.id).reset_execution_data()

    def finish(self) -> None:
        """
        Finish execution - update necessary variables, execute dependencies, and stop trigger.
        :return: None
        """
        st.StageStateMachine(self.model.id).validate_state(self.state, [st.PAUSING, st.RUNNING])
        logger.logger.info("Stage execution finished", stage_execution_id=self.model.id)

        self.state = st.FINISHED
        self.finish_time = timezone.now()
        self.execute_subjects_to_dependency()


def execution(execution_id: int) -> None:
    """
    Create StageExecution object and call its execute method
    :param execution_id: desired StageExecution's ID
    :return: None
    """
    logger.logger.debug("Starting Stage execution", stage_execution_id=execution_id)
    StageExecution(stage_execution_id=execution_id).execute()
    return None

import os
from datetime import datetime
from typing import Union, Type, Optional

from django.core import exceptions as django_exc
from django.db import transaction, connections
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict

from schema import Schema, Optional as SchemaOptional, SchemaError
from multiprocessing import Process

from cryton.hive.cryton_app.models import PlanModel, PlanExecutionModel, StageExecutionModel

from cryton.hive.utility import constants, exceptions, logger, scheduler_client, states as st
from cryton.hive.config.settings import SETTINGS
from cryton.hive.models import worker
from cryton.hive.models.stage import StageExecution, Stage
from django.utils import timezone


class Plan:
    def __init__(self, **kwargs):
        plan_model_id = kwargs.get('plan_model_id')
        if plan_model_id:
            try:
                self.model = PlanModel.objects.get(id=plan_model_id)
            except django_exc.ObjectDoesNotExist:
                raise exceptions.PlanObjectDoesNotExist(plan_id=plan_model_id)
        else:
            self.model = PlanModel.objects.create(**kwargs)

    def delete(self):
        self.model.delete()

    @property
    def model(self) -> Union[Type[PlanModel], PlanModel]:
        self.__model.refresh_from_db()
        return self.__model

    @model.setter
    def model(self, value: PlanModel):
        self.__model = value

    @property
    def name(self) -> str:
        return self.model.name

    @name.setter
    def name(self, value: str):
        model = self.model
        model.name = value
        model.save()

    @property
    def owner(self) -> str:
        return self.model.owner

    @owner.setter
    def owner(self, value: str):
        model = self.model
        model.owner = value
        model.save()

    @property
    def dynamic(self) -> bool:
        return self.model.dynamic

    @dynamic.setter
    def dynamic(self, value: bool):
        model = self.model
        model.dynamic = value
        model.save()

    @property
    def settings(self) -> dict:
        return self.model.settings

    @settings.setter
    def settings(self, value: dict):
        model = self.model
        model.settings = value
        model.save()

    @property
    def meta(self) -> dict:
        return self.model.meta

    @meta.setter
    def meta(self, value: dict):
        model = self.model
        model.meta = value
        model.save()
        
    @staticmethod
    def filter(**kwargs) -> QuerySet:
        """
        List PlanModel objects fulfilling fields specified in kwargs.
        If no such fields are specified all objects are returned.
        :param kwargs: dict of field-value pairs to filter by
        :raises WrongParameterError: invalid field is specified
        :return: Queryset of PlanModel objects
        """
        if kwargs:
            try:
                return PlanModel.objects.filter(**kwargs)
            except django_exc.FieldError as ex:
                raise exceptions.WrongParameterError(message=ex)
        return PlanModel.objects.all()

    @staticmethod
    def validate_unique_values(plan_dict) -> None:
        """
        Check if there are any duplicate names in Plan that should be unique
        :param plan_dict: Plan dictionary
        :raises
        exceptions.DuplicateNameInPlan:
        :return: None
        """
        stage_names = []
        step_names = []
        session_names = []
        agent_names = []

        for stage_dict in plan_dict.get('stages'):
            # validate unique stage names in plan
            if (stage_name := stage_dict['name']) in stage_names:
                raise exceptions.DuplicateNameInPlan(unique_argument="Stage", duplicate_name=stage_name,
                                                     plan_name=plan_dict.get("name"))
            stage_names.append(stage_name)

            if stage_dict.get(constants.TRIGGER_TYPE) == constants.MSF_LISTENER:
                session_names.append(f"{stage_name}_session")

            for step in stage_dict.get('steps'):
                # validate unique step names in plan
                if (step_name := step['name']) in step_names:
                    raise exceptions.DuplicateNameInPlan(unique_argument="Step", duplicate_name=step_name,
                                                         plan_name=plan_dict.get("name"))
                step_names.append(step_name)

                # validate unique empire agent names in plan
                if step[constants.STEP_TYPE] == constants.STEP_TYPE_DEPLOY_AGENT:
                    if (agent_name := step[constants.ARGUMENTS][constants.AGENT_NAME]) in agent_names:
                        raise exceptions.DuplicateNameInPlan(unique_argument="Empire Agent", duplicate_name=agent_name,
                                                             plan_name=plan_dict.get("name"))
                    agent_names.append(agent_name)

                if constants.CREATE_NAMED_SESSION in step[constants.ARGUMENTS]:
                    if (session_name := step[constants.ARGUMENTS][constants.CREATE_NAMED_SESSION]) in session_names:
                        raise exceptions.DuplicateNameInPlan(unique_argument="Session", duplicate_name=session_name,
                                                             plan_name=plan_dict.get("name"))
                    session_names.append(session_name)

    @staticmethod
    def validate(plan_dict, dynamic: bool = False) -> None:
        """
        Check if plan's dictionary is valid
        :param plan_dict: Plan information
        :param dynamic: If the Plan is static or dynamic
        :raises
            exceptions.PlanValidationError:
            exceptions.StageValidationError
            exceptions.StepValidationError
        :return: True if dictionary is valid
        """
        conf_schema = Schema({
            "name": str,
            SchemaOptional("owner"): str,
            SchemaOptional("dynamic"): bool,
            SchemaOptional("meta"): dict,
            SchemaOptional('settings'): {
                SchemaOptional(constants.SEPARATOR): str
            },
            "stages": list
        })

        try:
            logger.logger.debug("Validating plan", plan_name=plan_dict.get('name'))
            conf_schema.validate(plan_dict)
        except SchemaError as ex:
            raise exceptions.PlanValidationError(ex, plan_name=plan_dict.get("name"))

        # validate stages
        stage_names = []
        stage_dependencies = []
        for stage_dict in plan_dict.get("stages"):
            Stage.validate(stage_dict, dynamic)
            stage_names.append(stage_dict["name"])
            if "depends_on" in stage_dict.keys():
                stage_dependencies += stage_dict["depends_on"]

        # Check if there is at least one Stage when using static Plan
        if not dynamic and len(stage_names) == 0:
            raise exceptions.PlanValidationError("Plan has to contain at least one Stage.",
                                                 plan_name=plan_dict.get("name"))

        # validate stage dependencies
        for stage_dependency in set(stage_dependencies):
            if stage_dependency not in stage_names:
                raise exceptions.PlanValidationError(
                    f"Stage dependency '{stage_dependency}' does not exist in the "
                    f"plan", plan_name=plan_dict["name"])

        Plan.validate_unique_values(plan_dict)

    def generate_plan(self) -> dict:
        """
        Get Plan's YAML from database.
        :return: Plan and its Stages/Steps
        """
        stages = []
        for stage_obj in self.model.stages.all():
            steps = []
            for step_obj in stage_obj.steps.all():
                step_data = model_to_dict(step_obj, exclude=['stage_model'])

                successors = []
                for successor_obj in step_obj.successors.all():
                    successor_data = {'type': successor_obj.type, 'value': successor_obj.value,
                                      'step': successor_obj.successor.name}
                    successors.append(successor_data)

                step_data['next'] = successors
                steps.append(step_data)

            stage_data = model_to_dict(stage_obj, exclude=['plan_model'])
            stage_data['steps'] = steps
            stages.append(stage_data)

        plan_data = model_to_dict(self.model)
        plan_data['stages'] = stages

        return plan_data


class PlanExecution:
    def __init__(self, **kwargs):
        plan_execution_id = kwargs.get("plan_execution_id")
        if plan_execution_id is not None:
            try:
                self.model = PlanExecutionModel.objects.get(id=plan_execution_id)
            except django_exc.ObjectDoesNotExist:
                raise exceptions.PlanExecutionDoesNotExist(plan_execution_id=plan_execution_id)
        else:
            self.model = PlanExecutionModel.objects.create(**kwargs)
            self._prepare_executions()
            self._create_evidence_directory()

    def delete(self):
        self.model.delete()

    @property
    def model(self) -> Union[Type[PlanExecutionModel], PlanExecutionModel]:
        self.__model.refresh_from_db()
        return self.__model

    @model.setter
    def model(self, value: PlanExecutionModel):
        self.__model = value

    @property
    def state(self) -> str:
        return self.model.state

    @state.setter
    def state(self, value: str):
        with transaction.atomic():
            PlanExecutionModel.objects.select_for_update().get(id=self.model.id)
            if st.PlanStateMachine(self.model.id).validate_transition(self.state, value):
                logger.logger.debug("Plan execution changed state", state_from=self.state, state_to=value,
                                    plan_execution_id=self.model.id)
                model = self.model
                model.state = value
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
    def start_time(self) -> Optional[datetime]:
        return self.model.start_time

    @start_time.setter
    def start_time(self, value: Optional[datetime]):
        model = self.model
        model.start_time = value
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
    def aps_job_id(self) -> str:
        return self.model.aps_job_id

    @aps_job_id.setter
    def aps_job_id(self, value: str):
        model = self.model
        model.aps_job_id = value
        model.save()

    @property
    def evidence_directory(self) -> str:
        return self.model.evidence_directory

    @evidence_directory.setter
    def evidence_directory(self, value: str):
        model = self.model
        model.evidence_directory = value
        model.save()

    @property
    def all_stages_finished(self) -> bool:
        return not self.model.stage_executions.all().exclude(state__in=st.STAGE_FINAL_STATES).exists()

    def _create_evidence_directory(self) -> None:
        """
        Generate directory for storing execution evidence.
        :return: None
        """
        worker_evidence_directory = os.path.join(SETTINGS.evidence_directory, f"run_{self.model.run_id}",
                                                 f"worker_{self.model.worker.name}")

        os.makedirs(worker_evidence_directory, exist_ok=True)
        self.evidence_directory = worker_evidence_directory

    def _prepare_executions(self):
        """
        Prepare execution for each Stage.
        :return: None
        """
        stage_execution_kwargs = {'plan_execution': self.model}
        for stage_obj in self.model.plan_model.stages.all():
            stage_execution_kwargs.update({'stage_model': stage_obj})
            StageExecution(**stage_execution_kwargs)

    def schedule(self, schedule_time: datetime) -> None:
        """
        Schedule all plan's stages.
        :param schedule_time: Time to schedule to
        :return: None
        :raises
            :exception RuntimeError
        """
        # Check state
        logger.logger.debug("Scheduling Plan execution", plan_execution_id=self.model.id)
        st.PlanStateMachine(self.model.id).validate_state(self.state, st.PLAN_SCHEDULE_STATES)

        self.aps_job_id = scheduler_client.schedule_function("cryton.hive.lib.models.plan:execution", [self.model.id],
                                                             schedule_time)

        if isinstance(self.aps_job_id, str):
            self.schedule_time = schedule_time.replace(tzinfo=timezone.utc)
            self.state = st.SCHEDULED
            logger.logger.info("Plan execution scheduled", plan_execution_id=self.model.id, status='success')
        else:
            raise RuntimeError("Could not schedule Plan execution")

    def execute(self) -> None:
        """
        Execute Plan. This method starts triggers.
        :return: None
        """
        logger.logger.debug("Executing Plan", plan_execution_id=self.model.id)
        st.PlanStateMachine(self.model.id).validate_state(self.state, st.PLAN_EXECUTE_STATES)

        self.start_time = timezone.now()
        self.state = st.RUNNING

        # Prepare rabbit queues
        worker_obj = worker.Worker(worker_model_id=self.model.worker_id)
        worker_obj.prepare_rabbit_queues()

        # Start triggers
        self.start_triggers()
        logger.logger.info("Plan execution executed", plan_execution_id=self.model.id, status='success')

    def unschedule(self) -> None:
        """
        Unschedule plan execution.
        :return: None
        """
        logger.logger.debug("Unscheduling Plan execution", plan_execution_id=self.model.id)
        st.PlanStateMachine(self.model.id).validate_state(self.state, st.PLAN_UNSCHEDULE_STATES)

        scheduler_client.remove_job(self.aps_job_id)
        self.aps_job_id, self.schedule_time = "", None
        self.state = st.PENDING
        logger.logger.info("Plan execution unscheduled", plan_execution_id=self.model.id, status='success')

    def reschedule(self, new_time: datetime) -> None:
        """
        Reschedule plan execution.
        :param new_time: Time to reschedule to
        :raises UserInputError: when provided time < present
        :return: None
        """
        logger.logger.debug("Rescheduling Plan", plan_execution_id=self.model.id)
        st.PlanStateMachine(self.model.id).validate_state(self.state, st.PLAN_RESCHEDULE_STATES)

        if new_time < timezone.now():
            raise exceptions.UserInputError("Time argument must be greater or equal than current time.", str(new_time))

        self.unschedule()
        self.schedule(new_time)
        logger.logger.info("Plan execution rescheduled", plan_execution_id=self.model.id, status='success')

    def pause(self) -> None:
        """
        Pause plan execution.
        :return: None
        """
        logger.logger.debug("Pausing Plan", plan_execution_id=self.model.id)
        st.PlanStateMachine(self.model.id).validate_state(self.state, st.PLAN_PAUSE_STATES)

        self.state = st.PAUSING
        logger.logger.info("Plan execution pausing", plan_execution_id=self.model.id, status='success')

        for stage_ex in self.model.stage_executions.all():  # Pause StageExecutions.
            StageExecution(stage_execution_id=stage_ex.id).trigger.pause()

        if not self.model.stage_executions.exclude(state__in=st.PLAN_STAGE_PAUSE_STATES).exists():
            self.state = st.PAUSED
            self.pause_time = timezone.now()
            logger.logger.info("Plan execution paused", plan_execution_id=self.model.id, status='success')

    def unpause(self) -> None:
        logger.logger.debug("Unpausing Plan execution", plan_execution_id=self.model.id)
        st.PlanStateMachine(self.model.id).validate_state(self.state, st.PLAN_UNPAUSE_STATES)

        self.pause_time = None
        self.state = st.RUNNING

        for stage_execution_model in self.model.stage_executions.all():
            stage_ex = StageExecution(stage_execution_id=stage_execution_model.id)
            if stage_ex.model.stage_model.trigger_type == constants.DELTA \
                    and stage_ex.state in st.STAGE_SCHEDULE_STATES:
                stage_ex.trigger.start()
            else:
                try:
                    stage_ex.trigger.unpause()
                except exceptions.StageInvalidStateError:
                    pass

        logger.logger.info("Plan execution unpaused", plan_execution_id=self.model.id)

    def validate_modules(self):
        """
        For each stage validate if worker is up, all modules are present and module args are correct.
        """
        logger.logger.debug("Validating Plan execution modules", plan_execution_id=self.model.id)

        for stage_execution_id in self.model.stage_executions.values_list('id', flat=True):
            stage_execution = StageExecution(stage_execution_id=stage_execution_id)
            stage_execution.validate_modules()
        logger.logger.info("Plan execution modules validated", plan_execution_id=self.model.id)

        return None

    def start_triggers(self) -> None:
        """
        Start triggers for all execution stages.
        :return: None
        """
        logger.logger.debug("Starting triggers", plan_execution_id=self.model.id)
        for stage_execution_model in self.model.stage_executions.all():
            stage_execution = StageExecution(stage_execution_id=stage_execution_model.id)
            stage_execution.trigger.start()
            logger.logger.debug("Trigger started", plan_execution_id=self.model.id,
                                trigger=str(stage_execution.trigger))
        logger.logger.info("Triggers started", plan_execution_id=self.model.id, status='success')

    @staticmethod
    def filter(**kwargs) -> QuerySet:
        """
        List PlanExecutionModel objects fulfilling fields specified in kwargs.
        If no such fields are specified all objects are returned.
        :param kwargs: dict of field-value pairs to filter by
        :return: Queryset of PlanExecutionModel objects
        :raises WrongParameterError: invalid field is specified
        """
        if kwargs:
            try:
                return PlanExecutionModel.objects.filter(**kwargs)
            except django_exc.FieldError as ex:
                raise exceptions.WrongParameterError(message=ex)
        return PlanExecutionModel.objects.all()

    def report(self) -> dict:
        """
        Generate a report from Plan execution.
        :return: report from Plan execution
        """
        logger.logger.debug("Generating report", plan_execution_id=self.model.id)

        report_dict = dict()
        report_dict.update({'id': self.model.id, 'plan_name': self.model.plan_model.name,
                            'meta': self.model.plan_model.meta, 'state': self.state,
                            'schedule_time': self.schedule_time, 'start_time': self.start_time,
                            'finish_time': self.finish_time, 'pause_time': self.pause_time,
                            'worker_id': self.model.worker_id, 'worker_name': self.model.worker.name,
                            'evidence_directory': self.evidence_directory})
        report_dict.update({'stage_executions': []})
        for stage_execution_obj in StageExecutionModel.objects.filter(plan_execution_id=self.model.id).order_by('id'):
            stage_ex_report = StageExecution(stage_execution_id=stage_execution_obj.id).report()
            report_dict['stage_executions'].append(stage_ex_report)

        return report_dict

    def kill(self) -> None:
        """
        Kill current PlanExecution and its StageExecutions
        :return: None
        """
        logger.logger.debug("Killing Plan", plan_execution_id=self.model.id)
        st.PlanStateMachine(self.model.id).validate_state(self.state, st.PLAN_KILL_STATES)
        self.state = st.TERMINATING

        processes = list()

        # Unschedule Stage executions that can be unscheduled
        for stage_ex_model in self.model.stage_executions.filter(state__in=st.STAGE_UNSCHEDULE_STATES):
            stage_ex = StageExecution(stage_execution_id=stage_ex_model.id)
            process = Process(target=stage_ex.trigger.stop)
            processes.append(process)

        # Kill Stage executions that cannot be unscheduled
        for stage_ex_model in self.model.stage_executions.filter(state__in=st.STAGE_KILL_STATES):
            stage_ex = StageExecution(stage_execution_id=stage_ex_model.id)
            process = Process(target=stage_ex.kill)
            processes.append(process)

        connections.close_all()  # close connections to force each process to create its own
        for process in processes:
            process.start()

        for process in processes:
            process.join()

        self.finish_time = timezone.now()
        self.state = st.TERMINATED
        logger.logger.info("Plan execution killed", plan_execution_id=self.model.id,
                           plan_id=self.model.plan_model_id, status='success')

        return None

    def finish(self) -> None:
        """
        Finish execution - update necessary variables.
        :return: None
        """
        st.PlanStateMachine(self.model.id).validate_state(self.state, [st.PAUSING, st.RUNNING])
        logger.logger.info("Plan execution finished", plan_execution_id=self.model.id)

        self.state = st.FINISHED
        self.finish_time = timezone.now()


def execution(plan_execution_id: int) -> None:
    """
    Create PlanExecution object and call its execute method
    :param plan_execution_id: desired PlanExecutionModel's ID
    :return: None
    """
    PlanExecution(plan_execution_id=plan_execution_id).execute()
    return None

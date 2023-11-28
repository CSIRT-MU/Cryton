from typing import Union, Type, Optional, List
from datetime import datetime
from django.utils import timezone
from schema import Schema, SchemaError, Or, Optional as SchemaOptional
import copy
from threading import Thread

from django.db.models.query import QuerySet
from django.core import exceptions as django_exc
from django.db import transaction, connections

from cryton_core.cryton_app.models import StageModel, StageExecutionModel, StepExecutionModel, DependencyModel

from cryton_core.lib.util import exceptions, logger, states as st, util, constants

from cryton_core.lib.triggers import TriggerType, TriggerDelta, TriggerHTTP, TriggerMSF, TriggerDateTime

from cryton_core.lib.models.step import (
    StepExecution,
    StepExecutionWorkerExecute,
    Step,
    StepExecutionType
)

from cryton_core.etc import config

from dataclasses import dataclass, asdict


@dataclass
class StageReport:
    id: int
    name: str
    meta: dict
    state: str
    start_time: datetime
    pause_time: datetime
    finish_time: datetime
    schedule_time: datetime
    step_executions: list


class Stage:
    def __init__(self, **kwargs):
        """
        :param kwargs:
            stage_model_id: int = None,
            plan_model_id: int = None,
            name: str = None,
            trigger_type: str = None,
            trigger_args: dict = None
        """
        stage_model_id = kwargs.get('stage_model_id')
        if stage_model_id:
            try:
                self.model = StageModel.objects.get(id=stage_model_id)
            except django_exc.ObjectDoesNotExist:
                raise exceptions.StageObjectDoesNotExist(
                    "StageModel with id {} does not exist.".format(stage_model_id), stage_model_id
                )

        else:
            stage_obj_arguments = copy.deepcopy(kwargs)
            stage_obj_arguments.pop('depends_on', None)
            self.model = StageModel.objects.create(**stage_obj_arguments)

    def delete(self):
        self.model.delete()

    @property
    def model(self) -> Union[Type[StageModel], StageModel]:
        self.__model.refresh_from_db()
        return self.__model

    @model.setter
    def model(self, value: StageModel):
        self.__model = value

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
        return self.model.trigger_type

    @trigger_type.setter
    def trigger_type(self, value: str):
        model = self.model
        model.trigger_type = value
        model.save()

    @property
    def trigger_args(self) -> dict:
        return self.model.trigger_args

    @trigger_args.setter
    def trigger_args(self, value: dict):
        model = self.model
        model.trigger_args = value
        model.save()

    @property
    def meta(self) -> dict:
        return self.model.meta

    @meta.setter
    def meta(self, value: dict):
        model = self.model
        model.meta = value
        model.save()

    @property
    def final_steps(self) -> QuerySet:
        steps_list = Step.filter(stage_model_id=self.model.id, is_final=True)
        return steps_list

    @property
    def execution_list(self) -> QuerySet:
        """
        Returns StageExecutionModel QuerySet. If the latest is needed, use '.latest()' on result.
        :return: QuerySet of StageExecutionModel
        """
        return StageExecutionModel.objects.filter(stage_model_id=self.model.id)

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

    @staticmethod
    def _dfs_reachable(visited: set, completed: set, nodes_pairs: dict, node: str) -> set:
        """

        Depth first search of reachable nodes

        :param visited: set of visited nodes
        :param completed: set of completed nodes
        :param nodes_pairs: stage successors representation ({parent: [successors]})
        :param node: current node
        :return:
        """
        if node in visited and node not in completed:
            raise exceptions.StageCycleDetected("Stage cycle detected.")
        if node in completed:
            return completed
        visited.add(node)
        for neighbour in nodes_pairs.get(node, []):
            Stage._dfs_reachable(visited, completed, nodes_pairs, neighbour)
        completed.add(node)
        # completed and visited should be the same
        return completed

    @staticmethod
    def validate(stage_dict, dynamic: bool = False) -> bool:
        """
        Check if Stage's dictionary is valid
        :param stage_dict: Stage information
        :param dynamic: If the Plan is static or dynamic
        :raises
            exceptions.StageValidationError
            exceptions.StepValidationError
        :return True if Stage's dictionary is valid
        """
        conf_schema = Schema({
            'name': str,
            SchemaOptional("meta"): dict,
            'trigger_type': Or(*[trigger.name for trigger in list(TriggerType)]),
            'trigger_args': dict,
            'steps': list,
            SchemaOptional('depends_on'): list
        })

        try:
            logger.logger.debug("Validating stage", stage_name=stage_dict.get('name'))
            conf_schema.validate(stage_dict)
        except SchemaError as ex:
            raise exceptions.StageValidationError(ex, stage_name=stage_dict.get('name'))

        trigger = TriggerType[stage_dict.get('trigger_type')].value
        arg_schema = trigger.arg_schema
        try:
            arg_schema.validate(stage_dict.get('trigger_args'))
        except SchemaError as ex:
            raise exceptions.StageValidationError(ex, stage_name=stage_dict.get('name'))

        if not dynamic and len(stage_dict.get('steps')) == 0:
            raise exceptions.StageValidationError(
                'Stage cannot exist without steps!', stage_name=stage_dict.get('name'))

        steps_graph = dict()
        init_steps = set()
        all_steps_set = set()
        all_successors_set = set()
        for step_dict in stage_dict.get('steps'):
            Step.validate(step_dict)

            # Get needed information for reachability check
            if step_dict.get('is_init'):
                init_steps.add(step_dict.get('name'))
            succ_set = set()
            for succ_obj in step_dict.get('next', []):
                step_successors = succ_obj.get('step')
                if not isinstance(step_successors, list):
                    step_successors = [step_successors]
                succ_set.update(step_successors)
                steps_graph.update({step_dict.get('name'): succ_set})
            all_successors_set.update(succ_set)
            all_steps_set.add(step_dict.get('name'))

        # Check reachability
        reachable_steps_set = set()
        for init_step in init_steps:
            try:
                reachable_steps_set.update(Stage._dfs_reachable(set(), set(), steps_graph, init_step))
            except exceptions.StageCycleDetected:
                raise exceptions.StageValidationError("Cycle detected in Stage", stage_name=stage_dict.get('name'))
        if all_steps_set != reachable_steps_set:
            if len(reachable_steps_set) == 0:
                reachable_steps_set = None
            raise exceptions.StageValidationError(
                f'There is a problem with steps. Check that all steps are reachable, only existing steps are set as '
                f'successors, and at least one initial step exists. '
                f'All steps: {all_steps_set}, reachable steps: {reachable_steps_set}', )

        # Check that init steps are not set as successors
        if not init_steps.isdisjoint(all_successors_set):
            invalid_steps = init_steps.intersection(all_successors_set)
            raise exceptions.StageValidationError(
                f"One or more successors are set as init steps. Invalid steps are {invalid_steps}.")

        logger.logger.debug("Stage validated", stage_name=stage_dict.get('name'))
        return True

    def add_dependency(self, dependency_id: int) -> int:
        """
        Create dependency object
        :param dependency_id: Stage ID
        :return: ID of the dependency object
        """
        logger.logger.debug("Creating stage dependency", stage_id=self.model.id, dependency_id=dependency_id)
        dependency_obj = DependencyModel(stage_model_id=self.model.id, dependency_id=dependency_id)
        dependency_obj.save()
        logger.logger.debug("Stage dependency created", stage_id=self.model.id, dependency_id=dependency_id)

        return dependency_obj.id


class StageExecution:
    def __init__(self, **kwargs):
        """
        :param kwargs:
        (optional) stage_execution_id: int - for retrieving existing execution
        stage_model_id: int - for creating new execution
        """
        stage_execution_id = kwargs.get('stage_execution_id')
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
                logger.logger.debug("Stage execution changed state", state_from=self.state, state_to=value,
                                    stage_execution_id=self.model.id)
                model = self.model
                model.state = value
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
    def trigger(self) -> Union[TriggerDelta, TriggerHTTP, TriggerMSF, TriggerDateTime]:
        trigger_type = self.model.stage_model.trigger_type
        return TriggerType[trigger_type].value(stage_execution=self)

    @property
    def all_steps_finished(self) -> bool:
        return not self.model.step_executions.exclude(state__in=st.STEP_FINAL_STATES).exists()

    @property
    def all_dependencies_finished(self) -> bool:
        dependency_ids = self.model.stage_model.dependencies.all().values_list('dependency_id', flat=True)
        cond = self.filter(stage_model_id__in=dependency_ids, plan_execution_id=self.model.plan_execution_id) \
            .exclude(state=st.FINISHED).exists()

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
        step_execution_kwargs = {'stage_execution': self.model}
        for step_obj in self.model.stage_model.steps.all():
            step_execution_kwargs.update({'step_model': step_obj})
            StepExecution(**step_execution_kwargs)

    @staticmethod
    def _run_step_executions(step_executions: List[StepExecution]):
        """
        Evenly distribute Step executions and run each batch in a Process.
        :param step_executions: Step executions to be distributed into Processes
        :return: None
        """
        # Evenly distribute StepExecutions into processes.
        step_exec_lists = list(util.split_into_lists(step_executions, config.CPU_CORES))
        processes = []
        for step_executions in step_exec_lists:
            if step_executions:
                processes.append(logger.LoggedProcess(logg_queue=logger.logger_object.log_queue,
                                                      target=util.run_executions_in_threads, args=(step_executions,)))

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
        for step_ex_model in self.model.step_executions.filter(state=st.PENDING, step_model__is_init=True):
            step_executions.append(StepExecutionType[step_ex_model.step_model.step_type].
                                   value(step_execution_id=step_ex_model.id))

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

        logger.logger.info("Stage execution executed", stage_execution_id=self.model.id,
                           stage_name=self.model.stage_model.name, status='success')

    def validate_modules(self) -> None:
        """
        Check if module is present and module args are correct for each Step
        """
        logger.logger.debug("Validating stage modules", stage_execution_id=self.model.id)
        for step_ex_id in self.model.step_executions.filter(
                step_model__step_type=constants.STEP_TYPE_WORKER_EXECUTE).values_list('id', flat=True):
            StepExecutionWorkerExecute(step_execution_id=step_ex_id).validate()

        return None

    def report(self) -> dict:
        logger.logger.debug("Generating Stage report", stage_execution_id=self.model.id)
        report_obj = StageReport(id=self.model.id, name=self.model.stage_model.name, meta=self.model.stage_model.meta,
                                 state=self.state, schedule_time=self.schedule_time, start_time=self.start_time,
                                 finish_time=self.finish_time, pause_time=self.pause_time, step_executions=[])

        for step_execution_obj in StepExecutionModel.objects.filter(stage_execution_id=self.model.id).order_by('id'):
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
        logger.logger.info("Stage execution killed", stage_execution_id=self.model.id,
                           stage_name=self.model.stage_model.name, status='success')

    def execute_subjects_to_dependency(self) -> None:
        """
        Execute WAITING StageExecution subjects to specified StageExecution dependency.
        :return: None
        """
        logger.logger.debug("Executing Stage dependency subjects", stage_execution_id=self.model.id)
        subject_to_ids = self.model.stage_model.subjects_to.all().values_list('stage_model_id', flat=True)
        subject_to_exs = self.filter(stage_model_id__in=subject_to_ids,
                                     plan_execution_id=self.model.plan_execution_id,
                                     state=st.WAITING)
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
            model.aps_job_id = ""
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

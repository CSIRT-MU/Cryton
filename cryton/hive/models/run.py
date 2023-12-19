from typing import List, Optional, Union, Type
from datetime import datetime, timedelta
from threading import Thread

from django.db.models.query import QuerySet
from django.core import exceptions as django_exc
from django.db import transaction
from django.utils import timezone

from cryton.hive.cryton_app.models import RunModel, PlanExecutionModel, WorkerModel
from cryton.hive.utility import exceptions, logger, scheduler_client, states as st
from cryton.hive.models.plan import PlanExecution
from cryton.hive.models.worker import Worker

from dataclasses import dataclass, asdict


@dataclass
class RunReport:
    id: int
    plan_id: int
    plan_name: str
    state: str
    schedule_time: datetime
    start_time: datetime
    pause_time: datetime
    finish_time: datetime
    plan_executions: list


class Run:

    def __init__(self, **kwargs):
        """
        :param kwargs:
            run_id: int = None,
            plan_model_id: int
            workers: list
        """
        if kwargs.get('run_model_id'):
            run_id = kwargs.get('run_model_id')

            try:
                self.model = RunModel.objects.get(id=run_id)
            except django_exc.ObjectDoesNotExist:
                raise exceptions.RunObjectDoesNotExist(run_id=run_id)
            self.workers = [pex.worker for pex in self.model.plan_executions.all()]
        else:
            workers: list = kwargs.pop('workers', [])
            if not workers:
                raise exceptions.WrongParameterError(message="Parameter cannot be empty.", param_name="workers")

            self.workers = workers
            self.model = RunModel.objects.create(**kwargs)
            self._prepare_executions()

    def delete(self):
        """
        Delete RunModel
        :return:
        """
        logger.logger.debug("Deleting run", run_id=self.model.id)
        self.model.delete()

    @property
    def model(self) -> Union[Type[RunModel], RunModel]:
        """
        Get or set the RunModel.
        """
        self.__model.refresh_from_db()
        return self.__model

    @model.setter
    def model(self, value):
        self.__model = value

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
        """
        Get or set start time of RunModel.
        """
        return self.model.start_time

    @start_time.setter
    def start_time(self, value: Optional[datetime]):
        model = self.model
        model.start_time = value
        model.save()

    @property
    def pause_time(self) -> Optional[datetime]:
        """
        Get or set pause time of RunModel.
        """
        return self.model.pause_time

    @pause_time.setter
    def pause_time(self, value: Optional[datetime]):
        model = self.model
        model.pause_time = value
        model.save()

    @property
    def finish_time(self) -> Optional[datetime]:
        """
        Get or set pause time of RunModel.
        """
        return self.model.finish_time

    @finish_time.setter
    def finish_time(self, value: Optional[datetime]):
        model = self.model
        model.finish_time = value
        model.save()

    @property
    def state(self):
        """
        Get or set pause time of RunModel.
        """
        return self.model.state

    @state.setter
    def state(self, value: str):
        with transaction.atomic():
            RunModel.objects.select_for_update().get(id=self.model.id)
            if st.RunStateMachine(self.model.id).validate_transition(self.state, value):
                logger.logger.debug("run changed state", state_from=self.state, state_to=value, run_id=self.model.id)
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
    def workers(self) -> List[WorkerModel]:
        return self.__workers

    @workers.setter
    def workers(self, value: List[WorkerModel]):
        self.__workers = value

    @property
    def all_plans_finished(self) -> bool:
        return not self.model.plan_executions.all().exclude(state__in=st.PLAN_FINAL_STATES).exists()

    @staticmethod
    def filter(**kwargs) -> QuerySet:
        """
        Get list of RunModel according to no or specified conditions
        :param kwargs: dict of parameters to filter by
        :return:
        """
        logger.logger.debug("Filtering runs")
        if kwargs:
            try:
                return RunModel.objects.filter(**kwargs)
            except django_exc.FieldError as ex:
                raise exceptions.WrongParameterError(message=ex)
        else:
            return RunModel.objects.all()

    def _prepare_executions(self):
        """
        Prepare execution for each worker.
        :return: None
        """
        plan_execution_kwargs = {'run': self.model, 'plan_model_id': self.model.plan_model_id}
        for worker_obj in self.workers:
            plan_execution_kwargs.update({'worker': worker_obj})
            PlanExecution(**plan_execution_kwargs)

    def report(self) -> dict:
        report_obj = RunReport(id=self.model.id, plan_id=self.model.plan_model.id,
                               plan_name=self.model.plan_model.name, state=self.state,
                               schedule_time=self.schedule_time, start_time=self.start_time,
                               finish_time=self.finish_time, pause_time=self.pause_time, plan_executions=[])

        for plan_execution_obj in PlanExecutionModel.objects.filter(run_id=self.model.id).order_by('id'):
            plan_ex_report = PlanExecution(plan_execution_id=plan_execution_obj.id).report()
            report_obj.plan_executions.append(plan_ex_report)

        return asdict(report_obj)

    def schedule(self, schedule_time: datetime) -> None:
        """
        Schedules Run for specific time.
        :param schedule_time: Desired start time
        :return: None
        :raises
            :exception RuntimeError
        """
        logger.logger.debug("Scheduling Run", run_id=self.model.id)
        # Check state
        st.RunStateMachine(self.model.id).validate_state(self.state, st.RUN_SCHEDULE_STATES)

        # Schedule execution
        self.aps_job_id = scheduler_client.schedule_function("cryton.hive.lib.models.run:execution",
                                                             [self.model.id], schedule_time)
        if isinstance(self.aps_job_id, str):
            self.schedule_time = schedule_time.replace(tzinfo=timezone.utc)
            self.state = st.SCHEDULED
            logger.logger.info("Run scheduled", run_id=self.model.id, status='success')
        else:
            raise RuntimeError("Could not schedule run")

    def unschedule(self) -> None:
        """
        Unschedules Run on specified workers
        :return: None
        """
        logger.logger.debug("Unscheduling Run", run_id=self.model.id)
        # Check state
        st.RunStateMachine(self.model.id).validate_state(self.state, st.RUN_UNSCHEDULE_STATES)

        scheduler_client.remove_job(self.aps_job_id)
        self.aps_job_id, self.schedule_time = "", None
        self.state = st.PENDING
        logger.logger.info("Run unscheduled", run_id=self.model.id, status='success')

    def reschedule(self, schedule_time: datetime) -> None:
        """
        Reschedules Run on specified WorkerModels
        :param schedule_time: Desired start time
        :return: None
        """
        logger.logger.debug("Rescheduling Run", run_id=self.model.id)
        # Check state
        st.RunStateMachine(self.model.id).validate_state(self.state, st.RUN_RESCHEDULE_STATES)

        self.unschedule()
        self.schedule(schedule_time)

        logger.logger.info("Run rescheduled", run_id=self.model.id, status='success')

    def pause(self) -> None:
        """
        Pauses Run on specified WorkerModels
        :return:
        """
        logger.logger.debug("Pausing Run", run_id=self.model.id)
        # Check state
        st.RunStateMachine(self.model.id).validate_state(self.state, st.RUN_PAUSE_STATES)

        self.state = st.PAUSING

        for plan_ex in self.model.plan_executions.all():
            PlanExecution(plan_execution_id=plan_ex.id).pause()

        if not self.model.plan_executions.exclude(state__in=st.RUN_PLAN_PAUSE_STATES).exists():
            self.state = st.PAUSED
            self.pause_time = timezone.now()
            logger.logger.info("Run paused", run_id=self.model.id, status='success')

    def unpause(self) -> None:
        """
        Unpauses Run on specified WorkerModels
        :return:
        """
        logger.logger.debug("Unpausing Run", run_id=self.model.id)
        # Check state
        st.RunStateMachine(self.model.id).validate_state(self.state, st.RUN_UNPAUSE_STATES)

        self.pause_time = None
        self.state = st.RUNNING

        for plan_execution_model in self.model.plan_executions.all():
            PlanExecution(plan_execution_id=plan_execution_model.id).unpause()

        logger.logger.info("Run unpaused", run_id=self.model.id, status='success')

    def postpone(self, delta: timedelta) -> None:
        """
        Postpones Run on specified WorkerModels
        :param delta: Time delta
        :return:
        """
        logger.logger.debug("Postponing Run", run_id=self.model.id)
        # Check state
        st.RunStateMachine(self.model.id).validate_state(self.state, st.RUN_POSTPONE_STATES)

        schedule_time = self.schedule_time + delta

        self.unschedule()
        self.schedule(schedule_time)

        logger.logger.info("Run postponed", run_id=self.model.id, status='success')

    def healthcheck_workers(self) -> None:
        """
        Check if all Workers are alive.
        :raise ConnectionError: If a Worker is down.
        :return: None
        """
        for worker_model in self.workers:
            worker = Worker(worker_model_id=worker_model.id)
            if not worker.healthcheck():
                raise ConnectionError(f"Unable to get response from worker {worker.name} ({worker.model.id}).")

    def execute(self) -> None:
        """
        Executes Run
        :return:
        """
        logger.logger.debug("Executing Run", run_id=self.model.id)
        # Check state
        st.RunStateMachine(self.model.id).validate_state(self.state, st.RUN_EXECUTE_STATES)

        self.start_time = timezone.now()
        self.state = st.RUNNING

        # Execute Plan on every Slave
        for worker_obj in self.workers:
            plan_execution_model = self.model.plan_executions.get(worker_id=worker_obj.id)
            PlanExecution(plan_execution_id=plan_execution_model.id).execute()

        logger.logger.info("Run executed", run_id=self.model.id, status='success')

    def kill(self) -> None:
        """
        Kill current Run and its PlanExecutions
        :return: None
        """
        logger.logger.debug("Killing Run", run_id=self.model.id)
        st.RunStateMachine(self.model.id).validate_state(self.state, st.RUN_KILL_STATES)
        self.state = st.TERMINATING

        threads = list()

        # Unschedule Plan executions that can be unscheduled
        for plan_ex_obj in self.model.plan_executions.filter(state__in=st.PLAN_UNSCHEDULE_STATES):
            plan_ex = PlanExecution(plan_execution_id=plan_ex_obj.id)
            thread = Thread(target=plan_ex.unschedule)
            threads.append(thread)

        # Kill Plan executions that cannot be unscheduled
        for plan_ex_obj in self.model.plan_executions.filter(state__in=st.PLAN_KILL_STATES):
            plan_ex = PlanExecution(plan_execution_id=plan_ex_obj.id)
            thread = Thread(target=plan_ex.kill)
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.finish_time = timezone.now()
        self.state = st.TERMINATED
        logger.logger.info("Run killed", run_id=self.model.id, status='success')

        return None

    def validate_modules(self):
        """
        For each Plan validate if worker is up, all modules are present and module args are correct.
        """
        logger.logger.debug("Run modules validation started", run_id=self.model.id)

        for plan_execution_id in self.model.plan_executions.values_list('id', flat=True):
            plan_execution = PlanExecution(plan_execution_id=plan_execution_id)
            plan_execution.validate_modules()
        logger.logger.debug("Run modules validated", run_id=self.model.id)

        return None

    def finish(self) -> None:
        """
        Finish execution - update necessary variables.
        :return: None
        """
        st.RunStateMachine(self.model.id).validate_state(self.state, [st.PAUSING, st.RUNNING])
        logger.logger.info("Run finished", run_id=self.model.id)

        self.state = st.FINISHED
        self.finish_time = timezone.now()


def execution(run_model_id: int) -> None:
    """
    Create Run object and call its execute method
    :param run_model_id: desired RunModel's ID
    :return: None
    """
    Run(run_model_id=run_model_id).execute()
    return None

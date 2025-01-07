from typing import Type
from datetime import datetime
from threading import Thread

from django.db import transaction
from django.utils import timezone

from cryton.hive.cryton_app.models import RunModel
from cryton.hive.utility import logger, scheduler_client, states as st
from cryton.hive.models.plan import PlanExecution
from cryton.hive.models.worker import Worker
from cryton.hive.models.abstract import SchedulableExecution


class Run(SchedulableExecution):
    def __init__(self, model_id: int):
        """
        :param model_id: Model ID
        """
        self.__model = RunModel.objects.get(id=model_id)

    @staticmethod
    def create_model(plan_id: int) -> RunModel | Type[RunModel]:
        return RunModel.objects.create(plan_id=plan_id)

    @classmethod
    def prepare(cls, plan_id: int, worker_ids: list[int]) -> "Run":
        model = cls.create_model(plan_id)
        for worker_id in worker_ids:
            PlanExecution.prepare(plan_id, worker_id, model.id)

        return Run(model.id)

    def delete(self):
        """
        Delete RunModel
        :return:
        """
        logger.logger.debug("deleting run", run_id=self.model.id)
        self.model.delete()

    @property
    def model(self) -> Type[RunModel] | RunModel:
        self.__model.refresh_from_db()
        return self.__model

    @property
    def schedule_time(self) -> datetime | None:
        return self.model.schedule_time

    @schedule_time.setter
    def schedule_time(self, value: datetime | None):
        model = self.model
        model.schedule_time = value
        model.save()

    @property
    def start_time(self) -> datetime | None:
        """
        Get or set start time of RunModel.
        """
        return self.model.start_time

    @start_time.setter
    def start_time(self, value: datetime | None):
        model = self.model
        model.start_time = value
        model.save()

    @property
    def pause_time(self) -> datetime | None:
        """
        Get or set pause time of RunModel.
        """
        return self.model.pause_time

    @pause_time.setter
    def pause_time(self, value: datetime | None):
        model = self.model
        model.pause_time = value
        model.save()

    @property
    def finish_time(self) -> datetime | None:
        """
        Get or set pause time of RunModel.
        """
        return self.model.finish_time

    @finish_time.setter
    def finish_time(self, value: datetime | None):
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
            if st.RunStateMachine.validate_transition(self.state, value):
                logger.logger.debug("run changed state", state_from=self.state, state_to=value, run_id=self.model.id)
                model = self.model
                model.state = value
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
    def all_plans_finished(self) -> bool:
        return not self.model.plan_executions.all().exclude(state__in=st.PLAN_FINAL_STATES).exists()

    def report(self) -> dict:
        report_obj = dict(
            id=self.model.id,
            plan_id=self.model.plan.id,
            plan_name=self.model.plan.name,
            state=self.state,
            schedule_time=self.schedule_time,
            start_time=self.start_time,
            finish_time=self.finish_time,
            pause_time=self.pause_time,
            plan_executions=[],
        )

        for plan_execution_model in self.model.plan_executions.order_by("id"):
            plan_execution_report = PlanExecution(plan_execution_model.id).report()
            report_obj["plan_executions"].append(plan_execution_report)

        return report_obj

    def schedule(self, schedule_time: datetime) -> None:
        """
        Schedules Run for specific time.
        :param schedule_time: Desired start time
        :return: None
        :raises
            :exception RuntimeError
        """
        logger.logger.debug("scheduling run", run_id=self.model.id)
        st.RunStateMachine.validate_state(self.state, st.RUN_SCHEDULE_STATES)

        self.trigger_id = scheduler_client.schedule_function(
            "cryton.hive.models.run:execution", [self.model.id], schedule_time
        )
        if isinstance(self.trigger_id, str):
            self.schedule_time = schedule_time.replace(tzinfo=timezone.utc)
            self.state = st.SCHEDULED
            logger.logger.info("Run scheduled", run_id=self.model.id, status="success")
        else:
            raise RuntimeError("Could not schedule run")

    def unschedule(self) -> None:
        """
        Unschedules Run on specified workers
        :return: None
        """
        logger.logger.debug("Unscheduling Run", run_id=self.model.id)
        # Check state
        st.RunStateMachine.validate_state(self.state, st.RUN_UNSCHEDULE_STATES)

        scheduler_client.remove_job(self.trigger_id)
        self.trigger_id, self.schedule_time = "", None
        self.state = st.PENDING
        logger.logger.info("Run unscheduled", run_id=self.model.id, status="success")

    def reschedule(self, schedule_time: datetime) -> None:
        """
        Reschedules Run on specified WorkerModels
        :param schedule_time: Desired start time
        :return: None
        """
        logger.logger.debug("Rescheduling Run", run_id=self.model.id)
        # Check state
        st.RunStateMachine.validate_state(self.state, st.RUN_RESCHEDULE_STATES)

        self.unschedule()
        self.schedule(schedule_time)

        logger.logger.info("Run rescheduled", run_id=self.model.id, status="success")

    def pause(self) -> None:
        """
        Pauses Run on specified WorkerModels
        :return:
        """
        logger.logger.debug("Pausing Run", run_id=self.model.id)
        # Check state
        st.RunStateMachine.validate_state(self.state, st.RUN_PAUSE_STATES)

        self.state = st.PAUSING

        for plan_ex in self.model.plan_executions.all():
            PlanExecution(plan_ex.id).pause()

        if not self.model.plan_executions.exclude(state__in=st.RUN_PLAN_PAUSE_STATES).exists():
            self.state = st.PAUSED
            self.pause_time = timezone.now()
            logger.logger.info("Run paused", run_id=self.model.id, status="success")

    def resume(self) -> None:
        """
        Resumes Run on specified WorkerModels
        :return:
        """
        logger.logger.debug("Unpausing Run", run_id=self.model.id)
        # Check state
        st.RunStateMachine.validate_state(self.state, st.RUN_RESUME_STATES)

        self.pause_time = None
        self.state = st.RUNNING

        for plan_execution_model in self.model.plan_executions.all():
            PlanExecution(plan_execution_model.id).resume()

        logger.logger.info("Run resumed", run_id=self.model.id, status="success")

    def healthcheck_workers(self) -> None:
        """
        Check if all Workers are alive.
        :raise ConnectionError: If a Worker is down.
        :return: None
        """
        for plan_ex_model in self.model.plan_executions.all():
            worker = Worker(plan_ex_model.worker.id)
            if not worker.healthcheck():
                raise ConnectionError(f"Unable to get response from worker {worker.name} ({worker.model.id}).")

    def start(self) -> None:
        """
        Executes Run
        :return:
        """
        logger.logger.debug("Executing Run", run_id=self.model.id)
        st.RunStateMachine.validate_state(self.state, st.RUN_EXECUTE_STATES)

        self.start_time = timezone.now()
        self.state = st.RUNNING

        for plan_ex_model in self.model.plan_executions.all():
            PlanExecution(plan_ex_model.id).start()

        logger.logger.info("Run executed", run_id=self.model.id)

    def stop(self) -> None:
        """
        Stop current Run and its PlanExecutions
        :return: None
        """
        logger.logger.debug("stopping run", run_id=self.model.id)
        st.RunStateMachine.validate_state(self.state, st.RUN_STOP_STATES)
        self.state = st.STOPPING

        threads = list()
        # Unschedule Plan executions that can be unscheduled
        for plan_ex_obj in self.model.plan_executions.filter(state__in=st.PLAN_UNSCHEDULE_STATES):
            plan_ex = PlanExecution(plan_ex_obj.id)
            thread = Thread(target=plan_ex.unschedule)
            thread.start()
            threads.append(thread)

        # Stop Plan executions that cannot be unscheduled
        for plan_ex_obj in self.model.plan_executions.filter(state__in=st.PLAN_STOP_STATES):
            plan_ex = PlanExecution(plan_ex_obj.id)
            thread = Thread(target=plan_ex.stop)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        self.finish_time = timezone.now()
        self.state = st.STOPPED
        logger.logger.info("run stopped", run_id=self.model.id)

    def validate_modules(self):
        """
        For each Plan validate if worker is up, all modules are present and module args are correct.
        """
        logger.logger.debug("Run modules validation started", run_id=self.model.id)

        for plan_execution_id in self.model.plan_executions.values_list("id", flat=True):
            plan_execution = PlanExecution(plan_execution_id)
            plan_execution.validate_modules()
        logger.logger.debug("Run modules validated", run_id=self.model.id)

    def finish(self) -> None:
        """
        Finish execution - update necessary variables.
        :return: None
        """
        st.RunStateMachine.validate_state(self.state, [st.PAUSING, st.RUNNING])
        logger.logger.info("Run finished", run_id=self.model.id)

        self.state = st.FINISHED
        self.finish_time = timezone.now()


def execution(run_model_id: int) -> None:
    """
    Create Run object and call its execute method
    :param run_model_id: desired RunModel's ID
    :return: None
    """
    Run(run_model_id).start()

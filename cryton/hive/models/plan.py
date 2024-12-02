import os
from datetime import datetime
from typing import Type

from django.db import transaction, connections
from django.forms.models import model_to_dict

from multiprocessing import Process

from cryton.hive.cryton_app.models import PlanModel, PlanExecutionModel, StageExecutionModel, PlanSettings

from cryton.hive.utility import constants, exceptions, logger, scheduler_client, states as st
from cryton.hive.config.settings import SETTINGS
from cryton.hive.models.stage import StageExecution
from django.utils import timezone
from cryton.hive.models.abstract import Instance, SchedulableExecution
from cryton.hive.models.worker import Worker


class Plan(Instance):
    def __init__(self, model_id: int):
        """
        :param model_id: Model ID
        """
        self.__model = PlanModel.objects.get(id=model_id)

    @staticmethod
    def create_model(name: str, settings: dict, dynamic: bool, metadata: dict) -> PlanModel:
        return PlanModel.objects.create(
            name=name,
            metadata=metadata,
            settings=PlanSettings.objects.create(separator=settings.get("separator", ".")),
            dynamic=dynamic,
        )

    def delete(self):
        self.model.delete()

    @property
    def model(self) -> Type[PlanModel] | PlanModel:
        self.__model.refresh_from_db()
        return self.__model

    @property
    def name(self) -> str:
        return self.model.name

    @name.setter
    def name(self, value: str):
        model = self.model
        model.name = value
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
    def metadata(self) -> dict:
        return self.model.metadata

    @metadata.setter
    def metadata(self, value: dict):
        model = self.model
        model.metadata = value
        model.save()

    def generate_plan(self) -> dict:
        """
        Get Plan's YAML from database.
        :return: Plan and its Stages/Steps
        """
        stages = []
        for stage_obj in self.model.stages.all():
            steps = []
            for step_obj in stage_obj.steps.all():
                step_data = model_to_dict(step_obj, exclude=["stage"])

                successors = []
                for successor_obj in step_obj.successors.all():
                    successor_data = {
                        "type": successor_obj.type,
                        "value": successor_obj.value,
                        "step": successor_obj.successor.name,
                    }
                    successors.append(successor_data)

                step_data["next"] = successors
                steps.append(step_data)

            stage_data = model_to_dict(stage_obj, exclude=["plan"])
            stage_data["steps"] = steps
            stages.append(stage_data)

        plan_data = model_to_dict(self.model)
        plan_data["stages"] = stages

        return plan_data


class PlanExecution(SchedulableExecution):
    def __init__(self, model_id: int):
        """
        :param model_id: Model ID
        """
        self.__model = PlanExecutionModel.objects.get(id=model_id)

    @staticmethod
    def create_model(plan_id: int, worker_id: int, run_id: int) -> PlanExecutionModel | Type[PlanExecutionModel]:
        return PlanExecutionModel.objects.create(plan_id=plan_id, worker_id=worker_id, run_id=run_id)

    @classmethod
    def prepare(cls, plan_id: int, worker_id: int, run_id: int) -> "PlanExecution":
        model = cls.create_model(plan_id, worker_id, run_id)

        for stage in model.plan.stages.all():
            StageExecution.prepare(stage.id, model.id)

        return PlanExecution(model.id)

    def delete(self):
        self.model.delete()

    @property
    def model(self) -> Type[PlanExecutionModel] | PlanExecutionModel:
        self.__model.refresh_from_db()
        return self.__model

    @property
    def state(self) -> str:
        return self.model.state

    @state.setter
    def state(self, value: str):
        with transaction.atomic():
            PlanExecutionModel.objects.select_for_update().get(id=self.model.id)
            if st.PlanStateMachine.validate_transition(self.state, value):
                logger.logger.debug(
                    "Plan execution changed state",
                    state_from=self.state,
                    state_to=value,
                    plan_execution_id=self.model.id,
                )
                model = self.model
                model.state = value
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
    def start_time(self) -> datetime | None:
        return self.model.start_time

    @start_time.setter
    def start_time(self, value: datetime | None):
        model = self.model
        model.start_time = value
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
    def aps_job_id(self) -> str:
        return self.model.job_id

    @aps_job_id.setter
    def aps_job_id(self, value: str):
        model = self.model
        model.job_id = value
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

    def schedule(self, schedule_time: datetime) -> None:
        """
        Schedule all plan's stages.
        :param schedule_time: Time to schedule to
        :return: None
        :raises
            :exception RuntimeError
        """
        logger.logger.debug("Scheduling Plan execution", plan_execution_id=self.model.id)
        st.PlanStateMachine.validate_state(self.state, st.PLAN_SCHEDULE_STATES)

        self.aps_job_id = scheduler_client.schedule_function(
            "cryton.hive.models.plan:execution", [self.model.id], schedule_time
        )

        if isinstance(self.aps_job_id, str):
            self.schedule_time = schedule_time.replace(tzinfo=timezone.utc)
            self.state = st.SCHEDULED
            logger.logger.info("Plan execution scheduled", plan_execution_id=self.model.id, status="success")
        else:
            raise RuntimeError("Could not schedule Plan execution")

    def start(self) -> None:
        """
        Execute Plan. This method starts triggers.
        :return: None
        """
        logger.logger.debug("Executing Plan", plan_execution_id=self.model.id)
        st.PlanStateMachine.validate_state(self.state, st.PLAN_EXECUTE_STATES)

        # Create evidence directory
        self.evidence_directory = os.path.join(
            SETTINGS.evidence_directory, f"run_{self.model.run_id}", f"worker_{self.model.worker.name}"
        )
        os.makedirs(self.evidence_directory, exist_ok=True)
        Worker(self.model.worker_id).prepare_rabbit_queues()

        self.start_time = timezone.now()
        self.state = st.RUNNING

        for stage_execution_model in self.model.stage_executions.all():
            StageExecution(stage_execution_model.id).start()
        logger.logger.info("Plan execution executed", plan_execution_id=self.model.id, status="success")

    def unschedule(self) -> None:
        """
        Unschedule plan execution.
        :return: None
        """
        logger.logger.debug("Unscheduling Plan execution", plan_execution_id=self.model.id)
        st.PlanStateMachine.validate_state(self.state, st.PLAN_UNSCHEDULE_STATES)

        scheduler_client.remove_job(self.aps_job_id)
        self.aps_job_id, self.schedule_time = "", None
        self.state = st.PENDING
        logger.logger.info("Plan execution unscheduled", plan_execution_id=self.model.id, status="success")

    def reschedule(self, new_time: datetime) -> None:
        """
        Reschedule plan execution.
        :param new_time: Time to reschedule to
        :raises UserInputError: when provided time < present
        :return: None
        """
        logger.logger.debug("Rescheduling Plan", plan_execution_id=self.model.id)
        st.PlanStateMachine.validate_state(self.state, st.PLAN_RESCHEDULE_STATES)

        if new_time < timezone.now():
            raise exceptions.UserInputError("Time argument must be greater or equal than current time.", str(new_time))

        self.unschedule()
        self.schedule(new_time)
        logger.logger.info("Plan execution rescheduled", plan_execution_id=self.model.id, status="success")

    def pause(self) -> None:
        """
        Pause plan execution.
        :return: None
        """
        logger.logger.debug("Pausing Plan", plan_execution_id=self.model.id)
        st.PlanStateMachine.validate_state(self.state, st.PLAN_PAUSE_STATES)

        self.state = st.PAUSING
        logger.logger.info("Plan execution pausing", plan_execution_id=self.model.id, status="success")

        for stage_ex in self.model.stage_executions.all():  # Pause StageExecutions.
            StageExecution(stage_ex.id).pause()

        if not self.model.stage_executions.exclude(state__in=st.PLAN_STAGE_PAUSE_STATES).exists():
            self.state = st.PAUSED
            self.pause_time = timezone.now()
            logger.logger.info("Plan execution paused", plan_execution_id=self.model.id, status="success")

    def resume(self) -> None:
        logger.logger.debug("Unpausing Plan execution", plan_execution_id=self.model.id)
        st.PlanStateMachine.validate_state(self.state, st.PLAN_RESUME_STATES)

        self.pause_time = None
        self.state = st.RUNNING

        for stage_execution_model in self.model.stage_executions.all():
            stage_ex = StageExecution(stage_execution_model.id)
            if stage_ex.model.stage.type == constants.DELTA and stage_ex.state in [st.AWAITING]:
                stage_ex.start()
            else:
                try:
                    stage_ex.resume()
                except exceptions.InvalidStateError:
                    pass

        logger.logger.info("Plan execution resumed", plan_execution_id=self.model.id)

    def validate_modules(self):
        """
        For each stage validate if worker is up, all modules are present and module args are correct.
        """
        logger.logger.debug("Validating Plan execution modules", plan_execution_id=self.model.id)

        for stage_execution_id in self.model.stage_executions.values_list("id", flat=True):
            stage_execution = StageExecution(stage_execution_id)
            stage_execution.validate_modules()
        logger.logger.info("Plan execution modules validated", plan_execution_id=self.model.id)

    def report(self) -> dict:
        """
        Generate a report from Plan execution.
        :return: report from Plan execution
        """
        logger.logger.debug("Generating report", plan_execution_id=self.model.id)
        report_dict = dict(
            id=self.model.id,
            plan_name=self.model.plan.name,
            metadata=self.model.plan.metadata,
            state=self.state,
            schedule_time=self.schedule_time,
            start_time=self.start_time,
            finish_time=self.finish_time,
            pause_time=self.pause_time,
            worker_id=self.model.worker_id,
            worker_name=self.model.worker.name,
            evidence_directory=self.evidence_directory,
            stage_executions=[],
        )

        for stage_execution_obj in StageExecutionModel.objects.filter(plan_execution_id=self.model.id).order_by("id"):
            stage_ex_report = StageExecution(stage_execution_obj.id).report()
            report_dict["stage_executions"].append(stage_ex_report)

        return report_dict

    def stop(self) -> None:
        """
        Stop current PlanExecution and its StageExecutions
        :return: None
        """
        logger.logger.debug("Stoping Plan", plan_execution_id=self.model.id)
        st.PlanStateMachine.validate_state(self.state, st.PLAN_STOP_STATES)
        self.state = st.STOPPING

        processes = list()

        # Unschedule Stage executions that can be unscheduled
        for stage_ex_model in self.model.stage_executions.filter(state=st.AWAITING):
            stage_ex = StageExecution(stage_ex_model.id)
            process = Process(target=stage_ex.trigger.stop)
            processes.append(process)

        # Stop Stage executions that cannot be unscheduled
        for stage_ex_model in self.model.stage_executions.filter(state__in=st.STAGE_STOP_STATES):
            stage_ex = StageExecution(stage_ex_model.id)
            process = Process(target=stage_ex.stop)
            processes.append(process)

        connections.close_all()  # close connections to force each process to create its own
        for process in processes:
            process.start()

        for process in processes:
            process.join()

        self.finish_time = timezone.now()
        self.state = st.STOPPED
        logger.logger.info("Plan execution stoped", plan_execution_id=self.model.id, plan_id=self.model.plan.id)

    def finish(self) -> None:
        """
        Finish execution - update necessary variables.
        :return: None
        """
        st.PlanStateMachine.validate_state(self.state, [st.PAUSING, st.RUNNING])
        logger.logger.info("Plan execution finished", plan_execution_id=self.model.id)

        self.state = st.FINISHED
        self.finish_time = timezone.now()


def execution(plan_execution_id: int) -> None:
    """
    Create PlanExecution object and call its execute method
    :param plan_execution_id: desired PlanExecutionModel's ID
    :return: None
    """
    PlanExecution(plan_execution_id).start()

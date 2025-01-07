from datetime import datetime
import pytz
from queue import Empty
from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from cryton.hive.utility import logger, constants
from cryton.hive.config.settings import SETTINGS


class SchedulerService:

    def __init__(self, job_queue):
        self._job_queue = job_queue
        db_url = (
            f"postgresql://{SETTINGS.database.username}:{SETTINGS.database.password}@{SETTINGS.database.host}:"
            f"{SETTINGS.database.port}/{SETTINGS.database.name}"
        )

        jobstores = {"default": SQLAlchemyJobStore(url=db_url)}

        executors = {
            "default": ThreadPoolExecutor(SETTINGS.scheduler.max_threads),
        }

        job_defaults = {
            "coalesce": False,
            "max_instances": SETTINGS.scheduler.max_job_instances,
            "misfire_grace_time": SETTINGS.scheduler.misfire_grace_time,
        }

        self._scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=pytz.timezone(SETTINGS.timezone),
        )

    def start(self):
        self._scheduler.start()
        Thread(target=self.process_job_queue).start()

    def stop(self):
        self._scheduler.shutdown()

    def is_running(self):
        return self._scheduler.running

    def process_job_queue(self):
        while self._scheduler.running:
            try:
                job_details = self._job_queue.get(timeout=1)
            except Empty:
                continue

            action, request_pipe = job_details[0].get(constants.EVENT_ACTION), job_details[1]
            arguments = job_details[0].get("args")
            try:
                if action == constants.ADD_JOB:
                    result = self.exposed_add_job(**arguments)
                elif action == constants.ADD_REPEATING_JOB:
                    result = self.exposed_add_repeating_job(**arguments)
                elif action == constants.RESCHEDULE_JOB:
                    result = self.exposed_reschedule_job(**arguments)
                elif action == constants.PAUSE_JOB:
                    result = self.exposed_pause_job(**arguments)
                elif action == constants.RESUME_JOB:
                    result = self.exposed_resume_job(**arguments)
                elif action == constants.REMOVE_JOB:
                    result = self.exposed_remove_job(**arguments)
                elif action == constants.GET_JOBS:
                    result = self.exposed_get_jobs()
                elif action == constants.PAUSE_SCHEDULER:
                    result = self.exposed_pause_scheduler()
                elif action == constants.RESUME_SCHEDULER:
                    result = self.exposed_resume_scheduler()
                else:
                    raise RuntimeError("Unknown action")
            except Exception as ex:
                logger.logger.error("Scheduler could not process the request", error=str(ex))
                request_pipe.send("")
            else:
                request_pipe.send(result)

    def __del__(self):
        logger.logger.debug("scheduler deleted")

    def exposed_add_job(self, execute_function: str, function_args: list, start_time: datetime) -> str:
        """

        :param execute_function: Function/method to be scheduled
        :param function_args: Function arguments
        :param start_time: Function start time
        :return: Scheduled job ID
        """
        logger.logger.debug("Scheduling job in scheduler service", execute_function=execute_function)
        job_scheduled = self._scheduler.add_job(execute_function, "date", run_date=str(start_time), args=function_args)

        return job_scheduled.id

    def exposed_add_repeating_job(self, execute_function: str, seconds: int) -> str:
        """

        :param execute_function: Function/method to be scheduled
        :param seconds: Function interval in seconds
        :return: Scheduled job ID
        """
        logger.logger.debug("Scheduling repeating job in scheduler service", execute_function=execute_function)
        job_scheduled = self._scheduler.add_job(execute_function, "interval", seconds=seconds)
        return job_scheduled.id

    def exposed_reschedule_job(self, job_id: str):
        logger.logger.debug("Rescheduling job in scheduler service", job_id=job_id)
        return self._scheduler.reschedule_job(job_id)

    def exposed_pause_job(self, job_id: str):
        logger.logger.debug("Pausing job in scheduler service", job_id=job_id)
        return self._scheduler.pause_job(job_id)

    def exposed_resume_job(self, job_id: str):
        logger.logger.debug("Resuming job in scheduler service", job_id=job_id)
        return self._scheduler.resume_job(job_id)

    def exposed_remove_job(self, job_id: str):
        logger.logger.debug("Removing job in scheduler service", job_id=job_id)
        return self._scheduler.remove_job(job_id)

    def exposed_get_job(self, job_id: str):
        logger.logger.debug("Getting job in scheduler service", job_id=job_id)
        return self._scheduler.get_job(job_id)

    def exposed_get_jobs(self):
        logger.logger.debug("Getting multiple jobs in scheduler service")
        return self._scheduler.get_jobs()

    def exposed_pause_scheduler(self):
        logger.logger.debug("Pausing scheduler service")
        return self._scheduler.pause()

    def exposed_resume_scheduler(self):
        logger.logger.debug("Resuming scheduler service")
        return self._scheduler.resume()

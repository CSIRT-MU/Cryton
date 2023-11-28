import pickle
import threading

from django.core.management.base import BaseCommand
from django.db import connection

from cryton_core.lib.util import logger, scheduler_client
from cryton_core.lib.models import worker
# TODO: add this as a service to docker-compose


def monitor_health():
    logger.logger.info("Starting monitoring loop")
    worker_model_list = worker.WorkerModel.objects.all()
    for worker_model_obj in worker_model_list:
        logger.logger.info("Checking worker {}".format(worker_model_obj.id))
        t = threading.Thread(target=worker.Worker(worker_model_id=worker_model_obj.id).healthcheck)
        t.start()


class Command(BaseCommand):

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute('select job_state from apscheduler_jobs')
            for row in cursor.fetchall():
                job_dict = pickle.loads(row[0])
                if job_dict.get('func') == 'cryton_core.cryton_app.management.commands.startmonitoring:monitor_health':
                    logger.logger.info("Monitoring already scheduled")
                    return

        scheduler_client.schedule_repeating_function('cryton_core.cryton_app.management.'
                                                     'commands.startmonitoring:monitor_health', seconds=30)

        return None

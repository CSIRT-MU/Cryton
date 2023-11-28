from cryton_core.lib.services.listener import Listener

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        listener = Listener()
        listener.start()

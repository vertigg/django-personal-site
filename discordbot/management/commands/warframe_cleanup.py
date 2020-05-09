from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from discordbot.models import WFAlert


class Command(BaseCommand):
    help = 'Removes old alerts from db'

    def handle(self, *args, **options):
        delta = now() - timedelta(hours=3)
        WFAlert.objects.filter(created_at__lte=delta).delete()

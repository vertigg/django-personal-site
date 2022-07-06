from datetime import timedelta

from django.utils.timezone import now

from config.celery import app
from discordbot.models import WFAlert


@app.task()
def warframe_cleanup():
    """Removes outdated alerts from database"""
    delta = now() - timedelta(hours=3)
    WFAlert.objects.filter(created_at__lte=delta).delete()

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


def register_task(cls):
    """Shortcut function for registering class-based celery tasks"""
    return app.register_task(cls())

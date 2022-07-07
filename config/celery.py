import os
import time
from contextlib import contextmanager

from django.core.cache import cache

from celery import Celery, Task

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
TASK_LOCK_EXPIRE = 60 * 10

app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


def register_task(cls):
    """Shortcut function for registering class-based celery tasks"""
    return app.register_task(cls())


@contextmanager
def celery_task_lock(key: str, value: str, timeout: int = TASK_LOCK_EXPIRE):
    timeout_at = time.monotonic() + timeout - 3
    status = cache.add(key, value, timeout)
    try:
        yield status
    finally:
        if time.monotonic() < timeout_at and status:
            cache.delete(key)


class UniqueNamedTask(Task):
    """Celery Task class that allows only one task at time with specific name"""

    def __call__(self, *args, **kwargs):
        with celery_task_lock(self.name, self.request.id) as acquired:
            if acquired:
                return super().__call__(*args, **kwargs)
            raise Exception(f'Task {self.name} is already in progress')

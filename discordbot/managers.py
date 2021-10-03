import random
from datetime import timedelta

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.timezone import now


class PseudoRandomManager(models.Manager):
    """
    Custom manager for models with `pid` field. Used for 'pseudo' random
    discord bot commands
    """
    PID_WEIGHT_MAPPING = (
        (0, 0.33, (0, 125)),
        (1, 0.20, (125, 250)),
        (2, 0.15, (250, 500)),
        (3, 0.13, (500, 750)),
        (4, 0.1, (750, 1000)),
        (5, 0.09, (1000, 1500)),
    )
    PIDS = [x[0] for x in PID_WEIGHT_MAPPING]
    WEIGHTS = [x[1] for x in PID_WEIGHT_MAPPING]

    def contribute_to_class(self, model, name: str) -> None:
        self._check_columns(model)
        return super().contribute_to_class(model, name)

    def _is_pid_field(self, field):
        return isinstance(field, models.IntegerField) and field.attname == 'pid'

    def _check_columns(self, model):
        if not any([self._is_pid_field(field) for field in model._meta.fields]):
            raise ImproperlyConfigured(
                f'Model {model} is missing `pid` integer field and can '
                'not be used with PseudoRandomManager'
            )

    def refresh_weigted_pids(self):
        """
        Refreshes pid values across whole queryset, based on PID_WEIGHT_MAPPING
        """
        for pid, _, deltas in self.PID_WEIGHT_MAPPING:
            min_date = now() - timedelta(days=deltas[0])
            max_date = now() - timedelta(days=deltas[1])
            self.get_queryset().filter(
                date__lte=min_date, date__gte=max_date).update(pid=pid)

    def reset_pids(self):
        """Resets all `pid` fields to 0"""
        return self.get_queryset().update(pid=0)

    def get_random_entry(self):
        """
        Returns random entry based on `pid` field. This function sets field
        only to 0 or 1
        """
        qs = self.get_queryset().filter(deleted=False, pid=0).order_by('?')
        if qs.exists():
            obj = qs.first()
            obj.pid = 1
            obj.save()
            return obj
        if not self.get_queryset().exists():
            return f'No records for `{self.model._meta.object_name}` model'
        self.reset_pids()
        return self.get_random_entry()

    def get_random_weighted_entry(self, retries: int = 5):
        """
        Returns random entry based `pid` weight, which is calculated based
        on object timestamp. If specific PID does not exist in database,
        function will retry itself multiple times
        """
        # Failsafe in case we stuck in endless loop of misery
        if retries <= 0:
            return None
        pid = random.choices(self.PIDS, weights=self.WEIGHTS)[0]
        queryset = self.get_queryset().filter(deleted=False, pid=pid)
        if queryset.exists():
            return queryset.order_by('?').first()
        return self.get_random_weighted_entry(retries=retries - 1)

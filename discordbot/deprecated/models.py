from django.db import models
from django.utils.translation import gettext_lazy as _

from discordbot.managers import PseudoRandomManager
from main.models import BaseModel


class Brawl(models.Model):
    name = models.TextField(blank=True, null=True)
    action = models.TextField(blank=True, null=True)
    victim = models.TextField(blank=True, null=True)
    tool = models.TextField(blank=True, null=True)
    action2 = models.TextField(blank=True, null=True)
    place = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'discord_brawl'


class WFAlert(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    announced = models.BooleanField(default=False)
    content = models.TextField(blank=False, null=False)

    class Meta:
        verbose_name = 'Warframe Alert'
        verbose_name_plural = 'Warframe Alerts'
        db_table = 'discord_alerts'

    def __str__(self):
        return self.content


class WFSettingsMeta(models.base.ModelBase):
    alerts = {
        'orokin_reactor_bp': _('Orokin Reactor'),
        'orokin_catalyst_bp': _('Orokin Catalyst'),
        'forma_bp': _('Forma'),
        'exilus_ap': _('Exilus Adapter'),
        'fieldron': _('Fieldron'),
        'mutagen_mass': _('Mutagen Mass'),
        'mutalist_nav': _('Mutalist Alad V Nav Coordinate'),
        'detonite_injector': _('Detonite Injector'),
        'snipetron': _('Snipetron Vandal'),
        'twin_vipers': _('Twin Vipers Wraith'),
        'latron': _('Latron Wraith'),
        'strun': _('Strun Wraith'),
        'dera': _('Dera Vandal'),
        'karak': _('Karak Wraith'),
    }

    def __new__(cls, name, bases, attrs, **kwargs):
        for field, label in cls.alerts.items():
            attrs[field] = models.BooleanField(default=False, verbose_name=label)
        return super(WFSettingsMeta, cls).__new__(cls, name, bases, attrs, **kwargs)


class WFSettings(models.Model, metaclass=WFSettingsMeta):
    class Meta:
        db_table = 'discord_wf_settings'

    def reset_settings(self, commit=True):
        """Sets all fields to false and saves instance"""
        fields = list(self.__class__.alerts.keys())
        for field in fields:
            setattr(self, field, False)
        if commit:
            self.save()

    def __str__(self):
        if hasattr(self, 'discorduser'):
            return f'Settings for {self.discorduser} ({self.id})'
        return f'{self.id}'


class Gachi(BaseModel):
    pid = models.IntegerField(blank=True, null=True, default=0)
    url = models.URLField(unique=True, blank=True, null=True)
    objects = PseudoRandomManager()

    class Meta:
        db_table = 'discord_gachi'

    def __str__(self):
        return self.url

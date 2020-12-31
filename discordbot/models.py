import hashlib
import random
import urllib.parse as urllib
from datetime import timedelta
from urllib.parse import urlencode

from discord import Colour, Embed
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from discordbot.base.models import BaseModel


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
        (5, 0.9, (1000, 1500)),
    )
    PIDS = [x[0] for x in PID_WEIGHT_MAPPING]
    WEIGHTS = [x[1] for x in PID_WEIGHT_MAPPING]

    def _check_columns(self):
        if not any([isinstance(x, models.IntegerField) and x.attname == 'pid'
                    for x in self.model._meta.fields]):
            raise Exception(f'Model {self.model} does not have `pid` integer field')

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
        self._check_columns()
        return self.get_queryset().update(pid=0)

    def get_random_entry(self):
        """
        Returns random entry based on `pid` field. This function sets field
        only to 0 or 1
        """
        self._check_columns()
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

    def get_random_weighted_entry(self):
        """
        Returns random entry based `pid` weight, which is calculated based
        on object timestamp.
        """
        pid = random.choices(self.PIDS, weights=self.WEIGHTS)[0]
        return self.get_queryset().filter(deleted=False, pid=pid).order_by('?').first()


class WFAlert(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    created_at = models.DateTimeField(
        auto_now_add=True, blank=False, null=False)
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
        fields = [x.name for x in self._meta.fields if x.name != 'id']
        for field in fields:
            setattr(self, field, False)
        if commit:
            self.save()

    def __str__(self):
        if hasattr(self, 'discorduser'):
            return f'Settings for {self.discorduser} ({self.id})'
        return f'{self.id}'


class Brawl(models.Model):
    name = models.TextField(blank=True, null=True)
    action = models.TextField(blank=True, null=True)
    victim = models.TextField(blank=True, null=True)
    tool = models.TextField(blank=True, null=True)
    action2 = models.TextField(blank=True, null=True)
    place = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'discord_brawl'


class Gachi(BaseModel):
    pid = models.IntegerField(blank=True, null=True, default=0)
    url = models.URLField(unique=True, blank=True, null=True)
    objects = PseudoRandomManager()

    class Meta:
        db_table = 'discord_gachi'

    def __str__(self):
        return self.url


class DiscordLink(models.Model):
    key = models.CharField(unique=True, blank=False, null=True, max_length=20)
    url = models.URLField()

    class Meta:
        verbose_name_plural = 'Discord Links'
        db_table = 'discord_links'

    def __str__(self):
        return self.url

    @classmethod
    def get(cls, key, default=None):
        """Helper class method that returns url by given key"""
        try:
            obj = cls.objects.get(key=key)
            return obj.url
        except cls.DoesNotExist:
            if default:
                return default
            return f'Link with key `{key}` does not exist in database'


class DiscordSettings(models.Model):
    key = models.CharField(unique=True, blank=False, null=True, max_length=20)
    value = models.CharField(blank=False, null=True, max_length=50)

    class Meta:
        verbose_name_plural = 'Discord Settings'
        db_table = 'discord_settings'

    def __str__(self):
        return self.value


class DiscordUser(models.Model):

    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    wf_settings = models.OneToOneField(
        WFSettings, on_delete=models.SET_NULL, blank=True, null=True)

    id = models.BigIntegerField(
        "Discord ID",
        unique=True,
        blank=True,
        null=False,
        primary_key=True,
        help_text='Required. 18 characters, digits only.',
        validators=[RegexValidator(r'^\d{1,18}$')])
    display_name = models.TextField(
        "Username",
        max_length=40,
        help_text="Current discord display name")
    poe_profile = models.TextField(
        "PoE Account",
        blank=True,
        null=False,
        default='')
    admin = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        help_text="User can execute @admin commands")
    mod_group = models.BooleanField(
        "Moderator",
        default=False,
        blank=False,
        null=False,
        help_text="User can execute @mod commands")
    avatar_url = models.URLField(default=None, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Discord Users'
        db_table = 'discord_users'
        permissions = [
            ("can_update_ladder", "Can start ladder update"),
            ("can_add_wisdoms", "Can add wisdoms"),
        ]

    def __str__(self):
        return self.display_name

    @classmethod
    def is_admin(cls, discord_id):
        return cls.objects.filter(id=discord_id, admin=True).exists()

    @classmethod
    def is_moderator(cls, discord_id):
        return cls.objects.filter(id=discord_id, mod_group=True).exists()


class Wisdom(BaseModel):
    id = models.IntegerField(blank=True, null=False, primary_key=True)
    pid = models.IntegerField(db_column='pID', default=0)
    text = models.TextField(unique=True)
    author = models.ForeignKey(DiscordUser, on_delete=models.SET_NULL,
                               verbose_name="discord user", blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    objects = PseudoRandomManager()

    class Meta:
        db_table = 'discord_wisdoms'

    def __str__(self):
        return truncatechars(self.text, 50)


class MarkovText(models.Model):
    text = models.TextField()
    last_update = models.DateTimeField(blank=True, null=True, auto_now=False)
    key = models.BigIntegerField(help_text='Discord Channel ID', unique=True)

    def __str__(self):
        return f'<Markov Text Object: {self.key}>'


class DiscordImage(BaseModel):
    date = models.DateTimeField()
    image = models.ImageField(upload_to='images')
    checksum = models.CharField(max_length=32, editable=False, null=True)

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False,
             using=None, update_fields=None):
        if self.image:
            self.checksum = hashlib.md5(self.image.read()).hexdigest()
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    def __str__(self):
        if self.image:
            return self.image.name
        return f'Image {self.id}'


class MixImage(DiscordImage):
    pid = models.IntegerField(default=0)
    image = models.ImageField(upload_to='mix')
    author = models.ForeignKey(
        DiscordUser, on_delete=models.SET_NULL,
        null=True, verbose_name="discord user"
    )
    objects = PseudoRandomManager()

    class Meta:
        verbose_name = 'Mix Image'
        verbose_name_plural = 'Mix Images'

    def __str__(self):
        if self.image:
            return urllib.urljoin(settings.DEFAULT_DOMAIN, self.image.url)
        return f'Current DiscordMixImage {self.id} does not have attached file'


class MixPollEntry(BaseModel):
    image = models.ForeignKey(MixImage, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False, null=True)

    class Meta:
        verbose_name = 'Mix Poll Entry'
        verbose_name_plural = 'Mix Poll Entries'

    def __str__(self):
        return f'{self.user} {self.liked} {self.image}'


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'discorduser'):
        instance.discorduser.save()

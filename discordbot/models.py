import urllib.parse as urllib
import uuid
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
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CounterGroup(models.Model):
    name = models.CharField(max_length=20, unique=True, blank=False, null=True)
    title = models.CharField(max_length=20)
    latest_counter_id = models.PositiveIntegerField(blank=True, null=True)
    latest_counter_streak = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'<CounterGroup> {self.title}'

    def to_embed(self):
        return Embed(
            title=f'{self.title}',
            colour=Colour(0xff0074),
            description='\n'.join([x.to_message()
                                   for x in self.counters.all()])
        )


class Counter(models.Model):
    name = models.CharField(max_length=20, unique=True, blank=False, null=True)
    title = models.CharField(max_length=20)
    flavor_text = models.TextField(blank=True)
    value_description = models.TextField()
    value = models.IntegerField(default=0)
    group = models.ForeignKey(
        CounterGroup, on_delete=models.SET_NULL, blank=True, null=True, related_name='counters')

    def increment_value(self):
        self.value += 1
        self.save(update_fields=['value'])

    def decrement_value(self):
        self.value -= 1
        self.save(update_fields=['value'])

    def __str__(self):
        return f'{self.title}'

    def to_embed(self):
        return Embed(
            title=f'{self.title}',
            colour=Colour(0xff0074),
            description=f"{self.value_description}: {self.value}"
        )

    def to_message(self):
        return f"{self.value_description}: {self.value}"

    def _update_counter_group(self):
        if self.group.latest_counter_id == self.id:
            self.group.latest_counter_streak += 1
            self.group.save(update_fields=['latest_counter_streak'])
        else:
            self.group.latest_counter_id = self.id
            self.group.latest_counter_streak = 1
            self.group.save(
                update_fields=['latest_counter_id', 'latest_counter_streak'])

    def save(self, *args, **kwargs):
        if self.group:
            self._update_counter_group()
        super().save(*args, **kwargs)


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


class Gachi(models.Model):
    pid = models.IntegerField(blank=True, null=True, default=0)
    url = models.URLField(unique=True, blank=True, null=True)

    class Meta:
        db_table = 'discord_gachi'

    def __str__(self):
        return self.url


class DiscordPicture(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    pid = models.IntegerField(db_column='pID', default=0)
    url = models.URLField(unique=True)
    date = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'discord_pictures'


class DiscordLink(models.Model):
    key = models.CharField(unique=True, blank=False, null=True, max_length=20)
    url = models.URLField()

    class Meta:
        verbose_name_plural = 'Discord Links'
        db_table = 'discord_links'

    def __str__(self):
        return self.url


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
        WFSettings, on_delete=models.CASCADE, blank=True, null=True)
    token = models.CharField(unique=True, blank=True, null=True, max_length=20)

    id = models.IntegerField(
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

    steam_id = models.CharField(
        "Steam ID",
        blank=True,
        null=False,
        default='',
        max_length=17,
        validators=[RegexValidator(r'^\d{1,17}$')],
        help_text="17 characters, digits only.")

    blizzard_id = models.TextField(
        "Blizzard Tag",
        blank=True,
        null=False,
        default='',
        help_text="Example: Username-0000")

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

    def generate_new_token(self):
        while True:
            _new_token = uuid.uuid4().hex[:20].upper()
            if not (DiscordUser.objects
                    .filter(token=_new_token)
                    .exists()):
                break
        self.token = _new_token
        self.save(update_fields=['token'])

    def get_activation_url(self):
        self.generate_new_token()
        params = urllib.urlencode({'token': self.token})
        url = urllib.urljoin(settings.DEFAULT_DOMAIN, reverse('main:discord_link'))
        return f'{url}?{params}'


class Wisdom(models.Model):
    id = models.IntegerField(blank=True, null=False, primary_key=True)
    pid = models.IntegerField(db_column='pID', default=0)
    text = models.TextField(unique=True)
    author = models.ForeignKey(
        DiscordUser, on_delete=models.CASCADE, verbose_name="discord user")
    date = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        db_table = 'discord_wisdoms'

    def __str__(self):
        return truncatechars(self.text, 50)


class MarkovText(models.Model):
    text = models.TextField()
    last_update = models.DateTimeField(blank=True, null=True, auto_now=False)
    key = models.IntegerField(help_text='Discord Channel ID', unique=True)

    def __str__(self):
        return f'<Markov Text Object: {self.key}>'


class CoronaReportManager(models.Manager):
    def previous_report(self, instance_id, timestamp):
        try:
            return (self.get_queryset()
                    .filter(timestamp__lte=timestamp)
                    .exclude(id=instance_id)
                    .order_by('-timestamp')
                    .first())
        except (IndexError, ValueError):
            return None


class CoronaReport(models.Model):
    REPORT_FIELDS = ['confirmed', 'recovered', 'deaths']
    API_URL = 'https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/'
    API_ROOT = 'rest/services/ncov_cases/FeatureServer/1/query?'

    confirmed = models.IntegerField()
    recovered = models.IntegerField()
    deaths = models.IntegerField()
    timestamp = models.DateTimeField(auto_now=True)
    objects = CoronaReportManager()

    class Meta:
        ordering = ('-timestamp',)

    @classmethod
    def get_api_url(cls):
        return cls.API_URL + cls.API_ROOT + cls.query_data()

    @classmethod
    def query_data(cls):
        return urlencode({
            'outStatistics': [{
                "statisticType": "sum",
                "onStatisticField": field.capitalize(),
                "outStatisticFieldName": field} for field in cls.REPORT_FIELDS],
            'f': 'pjson'
        })

    @classmethod
    def get_footer(cls, other) -> str:
        return (
            f'Compared to report from '
            f'{other.timestamp.strftime("%Y-%m-%d %H-%M")}.\n'
        )

    @property
    def header(self) -> str:
        return (
            f'**Corona report from '
            f'{self.timestamp.strftime("%Y-%m-%d %H-%M")}**\n'
        )

    @property
    def single_report(self) -> Embed:
        report_fields = [f'Total {field.capitalize()}: {getattr(self, field)}'
                         for field in self.REPORT_FIELDS]
        embed = Embed(
            title=self.header,
            colour=Colour(0xff0074),
            description='\n'.join(report_fields) + f'\n\n{self.get_chart_url()}'
        )
        embed.set_footer(text=f'Based on single report from {self.timestamp}')
        return embed

    @classmethod
    def get_chart_url(cls):
        return urllib.urljoin(
            settings.DEFAULT_DOMAIN, reverse('discordbot:corona_report')
        )

    @classmethod
    def generate_embed_report(cls, instance=None, other=None) -> Embed:
        """Calculates difference with previous report, either automatically
        or by sending previous report manually

        Args:
            instance (CoronaReport, optional): First instance of CoronaReport
            other (CoronaReport, optional): Another instance of CoronaReport
            Defaults to None.
        Returns:
            Formatted message for Discord chat
        """
        if not instance:
            instance = cls.objects.first()
            if not instance:
                return 'Not enough data gathered. Please try again in an hour'

        if not other:
            other = cls.objects.previous_report(instance.id, instance.timestamp)
            # If no previous report was found - send normal message
            if not other:
                return instance.single_report

        if not isinstance(other, CoronaReport):
            raise Exception(
                f'Can not calculate difference between {instance} and {other}'
            )
        if other.timestamp >= instance.timestamp:
            raise Exception(
                f'Instance timestamp should be greater than {other} timestamp'
            )

        report_strings = []
        for field in cls.REPORT_FIELDS:
            field_string = ''
            old_value = getattr(other, field)
            new_value = getattr(instance, field)
            diff = new_value - old_value
            field_string += f'Total {field.capitalize()}: {new_value}'
            if diff != 0:
                proc_diff = round((new_value - old_value) / old_value, 2)
                sign = '+' if diff > 0 else '-'
                field_string += f' ({sign}{diff})({sign}{proc_diff}%)'
            report_strings.append(field_string)
        embed = Embed(
            title=instance.header,
            colour=Colour(0xff0074),
            description='\n'.join(report_strings),
        )
        embed.description += f'\n\n{cls.get_chart_url()}'
        embed.set_footer(text=cls.get_footer(other))
        return embed

    def __str__(self):
        return f'Corona Report: {self.timestamp.strftime("%Y-%m-%d %H-%M")}'


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'discorduser'):
        instance.discorduser.save()

import hashlib
import urllib.parse as urllib

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy as _

from discordbot.base.models import BaseModel
from discordbot.managers import PseudoRandomManager


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
        fields = list(self.__class__.alerts.keys())
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

    @classmethod
    def get_setting(cls, key, default=None):
        try:
            obj = cls.objects.get(key=key)
            return obj.value
        except cls.DoesNotExist:
            if default:
                return default
            raise cls.DoesNotExist(f'There is no such setting with key {key}')


class DiscordUser(models.Model):
    id = models.BigIntegerField(
        "Discord ID",
        unique=True,
        blank=True,
        null=False,
        primary_key=True,
        help_text='Required. 18 characters, digits only.',
        validators=[RegexValidator(r'^\d{1,18}$')]
    )
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    wf_settings = models.OneToOneField(
        WFSettings,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    display_name = models.TextField(
        "Username",
        max_length=40,
        help_text="Current discord display name"
    )
    poe_profile = models.TextField(
        "PoE Account",
        blank=True,
        null=False,
        default=''
    )
    admin = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        help_text="User can execute @admin commands"
    )
    mod_group = models.BooleanField(
        "Moderator",
        default=False,
        blank=False,
        null=False,
        help_text="User can execute @mod commands"
    )
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
    author = models.ForeignKey(
        DiscordUser, on_delete=models.SET_NULL,
        verbose_name="discord user", blank=True, null=True
    )
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
    date = models.DateTimeField(auto_now_add=True)
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

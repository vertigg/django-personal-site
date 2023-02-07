import hashlib
import urllib.parse as urllib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import truncatechars

from discordbot.managers import PseudoRandomManager
from main.models import BaseModel

User = get_user_model()


class KeyValueModelMeta(models.base.ModelBase):

    def __getitem__(cls, key, default=None):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist as exc:
            if default:
                return default
            raise KeyError(f'There is no such setting with key {key}') from exc

    def __setitem__(cls, key: str, value: str):
        return cls.objects.update_or_create(key=key, defaults={'value': value})

    def __delitem__(cls, key):
        return cls.objects.filter(key=key).delete()

    def get(cls, key: str, default: str = None):
        return cls.__getitem__(key, default)

    def set(cls, key: str, value: str):
        item, _ = cls.__setitem__(key, value)
        return item


class KeyValueModel(models.Model, metaclass=KeyValueModelMeta):
    """
    Model with key and value char fields and dictionary like interface for 
    setting, getting and deleting values.
    """
    key = models.CharField(unique=True, blank=False, null=True, max_length=20)
    value = models.CharField(blank=False, null=True, max_length=50)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.value


class DiscordLink(KeyValueModel):
    value = models.URLField()

    class Meta:
        verbose_name_plural = 'Discord Links'
        db_table = 'discord_links'


class DiscordSettings(KeyValueModel):

    class Meta:
        verbose_name_plural = 'Discord Settings'
        db_table = 'discord_settings'


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

    @classmethod
    def get_cached_nicknames(cls) -> dict[int, str]:
        return {
            id: display_name for id, display_name in
            cls.objects.values_list('id', 'display_name')
        }


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


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'discorduser'):
        instance.discorduser.save()

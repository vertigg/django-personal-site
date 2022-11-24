from discordbot.models import DiscordUser
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now
from main.models import BaseModel


class PoeInfo(models.Model):
    key = models.TextField(primary_key=True, blank=False, null=False, unique=True)
    value = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)


class League(models.Model):
    id = models.AutoField(blank=True, null=False, primary_key=True)
    name = models.TextField(blank=False, null=False)
    url = models.URLField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    slug = models.SlugField(null=True, default=None)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'League'
        verbose_name_plural = 'Leagues'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('poe:ladder_url', kwargs={'slug': self.slug})


class ActiveGem(models.Model):
    name = models.CharField(max_length=40)
    icon = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Gem'
        verbose_name_plural = 'Gems'
        ordering = ('name',)


class Character(BaseModel):
    id = models.AutoField(blank=True, null=False, primary_key=True)
    name = models.TextField(unique=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    class_name = models.TextField(max_length=30)
    class_id = models.PositiveIntegerField(blank=True, null=True)
    ascendancy_id = models.PositiveIntegerField(blank=True, null=True)
    level = models.PositiveIntegerField(blank=True, null=True)
    gems = models.ManyToManyField(ActiveGem)
    experience = models.BigIntegerField(blank=True, null=True)
    profile = models.ForeignKey(DiscordUser, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'

    def __str__(self):
        return f'{self.name}: {self.level} level'


class Announcement(BaseModel):
    release_date = models.DateTimeField()
    text = models.TextField()

    @classmethod
    def get_next_announcement(cls):
        return cls.objects.order_by('release_date').filter(
            release_date__gte=now()).first()

    def __str__(self) -> str:
        return str(self.release_date)

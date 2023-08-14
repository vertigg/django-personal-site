from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now

from discordbot.models import DiscordUser
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


class Item(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    icon = models.URLField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class Character(BaseModel):

    class ExperienceTrend(models.IntegerChoices):
        NO_CHANGE = 0, 'No changes'
        UPWARD = 1, 'Player has more experience since last update'
        DOWNWARD = 2, 'Player has less experience since last update'

    id = models.AutoField(blank=True, null=False, primary_key=True)
    name = models.TextField(unique=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    class_name = models.TextField(max_length=30)
    class_id = models.PositiveIntegerField(blank=True, null=True)
    ascendancy_id = models.PositiveIntegerField(blank=True, null=True)
    level = models.PositiveIntegerField(blank=True, null=True)
    experience = models.BigIntegerField(blank=True, null=True)
    profile = models.ForeignKey(DiscordUser, on_delete=models.CASCADE)
    expired = models.BooleanField(default=False)
    gems = models.ManyToManyField(ActiveGem)
    items = models.ManyToManyField(Item, blank=True)
    experience_trend = models.PositiveSmallIntegerField(
        choices=ExperienceTrend.choices,
        default=ExperienceTrend.NO_CHANGE
    )

    # Experimental fields
    life = models.PositiveSmallIntegerField(null=True)
    es = models.PositiveSmallIntegerField(null=True, verbose_name='Energy Shield')
    combined_dps = models.FloatField(null=True)

    class Meta:
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'

    def __str__(self):
        return f'{self.name}: Level {self.level} {self.class_name}'

    def get_experience_trend(self, new_value: int):
        if self.experience == new_value:
            return self.ExperienceTrend.NO_CHANGE
        if self.experience < new_value:
            return self.ExperienceTrend.UPWARD
        return self.ExperienceTrend.DOWNWARD


class Announcement(BaseModel):
    release_date = models.DateTimeField()
    text = models.TextField()

    @classmethod
    def get_next_announcement(cls):
        return cls.objects.order_by('release_date').filter(
            release_date__gte=now()).first()

    def __str__(self) -> str:
        return str(self.release_date)

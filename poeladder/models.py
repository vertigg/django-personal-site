from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from discordbot.models import DiscordUser


class PoeInfo(models.Model):
    key = models.TextField(primary_key=True, blank=False,
                           null=False, unique=True)
    value = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'poeladder_info'


class PoeLeague(models.Model):
    id = models.AutoField(blank=True, null=False, primary_key=True)
    name = models.TextField(blank=False, null=False)
    url = models.URLField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    slug = models.SlugField(null=True, default=None)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(PoeLeague, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'League'
        verbose_name_plural = 'Leagues'
        db_table = 'poeladder_leagues'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('poeladder:ladder_url', kwargs={'slug': self.slug})


class PoeActiveGem(models.Model):
    name = models.CharField(max_length=40)
    icon = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Gem'
        verbose_name_plural = 'Gems'
        db_table = 'poeladder_gems'
        ordering = ('name',)


class PoeCharacter(models.Model):
    id = models.AutoField(blank=True, null=False, primary_key=True)
    name = models.TextField(unique=True)
    league = models.ForeignKey(PoeLeague, on_delete=models.CASCADE)
    class_name = models.TextField(max_length=30)
    class_id = models.IntegerField(blank=True, null=True)
    ascendancy_id = models.IntegerField(blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    gems = models.ManyToManyField(PoeActiveGem)
    experience = models.BigIntegerField(blank=True, null=True)
    profile = models.ForeignKey(DiscordUser, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'
        db_table = 'poeladder_characters'

    def __str__(self):
        return self.name

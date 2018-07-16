from django.db import models
from discordbot.models import DiscordUser
from django.urls import reverse


class PoeInfo(models.Model):
    key = models.TextField(primary_key=True, blank=False, null=False, unique=True)
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

    class Meta:
        verbose_name_plural = 'Leagues'
        db_table = 'poeladder_leagues'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('league_ladder_view', kwargs={'league':self.name}, current_app='poeladder')

class PoeActiveGem(models.Model):
    name = models.CharField(max_length=40)
    icon = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
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
        verbose_name_plural = 'Characters'
        db_table = 'poeladder_characters'

    def __str__(self):
        return self.name

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
        db_table = 'poeladder_leagues'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('league_ladder_view', kwargs={'league':self.name}, current_app='poeladder')


class PoeCharacter(models.Model):
    id = models.AutoField(blank=True, null=False, primary_key=True)
    name = models.TextField(unique=True)
    league = models.ForeignKey(PoeLeague, on_delete=models.CASCADE)
    class_name = models.TextField(max_length=30)
    class_id = models.IntegerField(blank=True, null=True)
    ascendancy_id = models.IntegerField(blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    profile = models.ForeignKey(DiscordUser, on_delete=models.CASCADE)

    class Meta:
        db_table = 'poeladder_characters'

    def __str__(self):
        return self.name

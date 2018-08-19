from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

REGIONS = (
    ('eu', 'Europe'),
    ('us', 'United States'),
    ('kr', 'Korea'),
    ('tw', 'Taiwan'),
    ('sea', 'Southeast Asia'),
)


class WOWSettings(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    track_2v2 = models.BooleanField(default=True)
    track_3v3 = models.BooleanField(default=True)
    track_rbg = models.BooleanField(default=True)
    track_skirmish = models.BooleanField(default=True)
    track_unknown = models.BooleanField(default=True)
    public_view = models.BooleanField(default=True)

    class Meta:
        db_table = 'wow_settings'

    def __str__(self):
        return "<WOWSettings objects for {}>".format(self.user)


class WOWAccount(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    btag = models.CharField(unique=True, blank=True, null=True, max_length=50)
    bnet_id = models.IntegerField(blank=True, null=True)
    token = models.CharField(unique=True, blank=True, null=True, max_length=20)
    register_date = models.DateTimeField(auto_now_add=True, blank=True)
    region = models.CharField(max_length=3, choices=REGIONS, default='eu')

    class Meta:
        db_table = 'wow_accounts'
        verbose_name = 'WOW Account'
        verbose_name_plural = 'WOW Accounts'

    def __str__(self):
        return self.btag

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not hasattr(self.user, 'wowsettings'):
            WOWSettings.objects.create(user=self.user)
        return super().save(force_insert, force_update, using, update_fields)


class WOWCharacter(models.Model):

    account = models.ForeignKey(WOWAccount, on_delete=models.CASCADE)
    name = models.CharField(blank=True, null=True, max_length=50)
    realm = models.CharField(blank=True, null=True, max_length=50)
    battlegroup = models.CharField(blank=True, null=True, max_length=50)
    level = models.IntegerField(blank=True, null=True)
    character_class = models.IntegerField(blank=True, null=True)
    race = models.IntegerField(blank=True, null=True)
    gender = models.IntegerField(blank=True, null=True)
    achievement_points = models.IntegerField(blank=True, null=True)
    thumbnail = models.URLField()
    last_modified = models.IntegerField(blank=True, null=True)
    track = models.BooleanField(default=True)
    guild = models.CharField(blank=True, null=True, max_length=50)

    class Meta:
        db_table = 'wow_characters'
        verbose_name = 'WOW Character'
        verbose_name_plural = 'WOW Characters'

    def __str__(self):
        return self.name


class PVPBracket(models.Model):
    slug = models.SlugField(max_length=10)
    rating = models.IntegerField(blank=True, null=True)
    weekly_played = models.IntegerField(blank=True, null=True)
    weekly_won = models.IntegerField(blank=True, null=True)
    weekly_lost = models.IntegerField(blank=True, null=True)
    season_played = models.IntegerField(blank=True, null=True)
    season_won = models.IntegerField(blank=True, null=True)
    season_lost = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "PVP Bracket"
        verbose_name_plural = "PVP Brackets"
        db_table = 'wow_brackets'

    def __str__(self):
        return "<PVP Bracket {}>".format(self.slug)


class WOWStatSnapshot(models.Model):

    character = models.ForeignKey(WOWCharacter, on_delete=models.CASCADE)
    honorable_kills = models.IntegerField(blank=True, null=True)
    arena_2v2 = models.ForeignKey(
        PVPBracket,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='arena_2v2')
    arena_3v3 = models.ForeignKey(
        PVPBracket,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='arena_3v3')
    arena_rbg = models.ForeignKey(
        PVPBracket,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='arena_rbg')
    arena_unknown = models.ForeignKey(
        PVPBracket,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='arena_unknown')
    arena_skirmish = models.ForeignKey(
        PVPBracket,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='arena_skirmish')
    snapshot_date = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        db_table = 'wow_stats'

    def __str__(self):
        return "<{0}: {1}>".format(self.character, self.snapshot_date)

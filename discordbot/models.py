from django.db import models


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
    pid = models.IntegerField(db_column='pID', default=0)  # Field name made lowercase.
    url = models.URLField(unique=True)
    date = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'discord_pictures'


class DiscordLink(models.Model):
    key = models.TextField()
    url = models.URLField()

    class Meta:
        db_table = 'discord_links'

    def __str__(self):
        return self.url


class DiscordSettings(models.Model):
    key = models.TextField(unique=True, blank=True, null=True)
    value = models.TextField()

    class Meta:
        verbose_name_plural = 'Discord Settings'
        db_table = 'discord_settings'

    def __str__(self):
        return self.value

class DiscordUser(models.Model):
    id = models.TextField(unique=True, 
        blank=True, 
        null=False, 
        primary_key=True,
        max_length=25)
    display_name = models.TextField(unique=True, max_length=40)
    steam_id = models.IntegerField(blank=True, null=True)
    blizzard_id = models.TextField(blank=True, null=True)
    poe_profile = models.TextField(blank=True, null=True)
    admin = models.IntegerField(blank=True, null=True, default=0)
    mod_group = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        db_table = 'discord_users'

    def __str__(self):
        return self.display_name


class Wisdom(models.Model):
    id = models.IntegerField(blank=True, null=False, primary_key=True)
    pid = models.IntegerField(db_column='pID', default=0)
    text = models.TextField(unique=True)
    author = models.ForeignKey(DiscordUser,
         on_delete=models.CASCADE, 
         verbose_name="discord user")
    date = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        db_table = 'discord_wisdoms'

    def __str__(self):
        return self.text
            

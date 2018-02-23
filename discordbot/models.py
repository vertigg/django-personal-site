from django.db import models


class Brawl(models.Model):
    names = models.TextField(blank=True, null=True)
    actions = models.TextField(blank=True, null=True)
    victims = models.TextField(blank=True, null=True)
    tools = models.TextField(blank=True, null=True)
    actions2 = models.TextField(blank=True, null=True)
    places = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'brawl'


class CachedNicknames(models.Model):
    id = models.TextField(unique=True, primary_key=True, null=False)
    display_name = models.TextField(blank=True, null=True)
    date = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cached_nicknames'


class Gachi(models.Model):
    pid = models.IntegerField(blank=True, null=True)
    url = models.URLField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gachi'


class Imgur(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    pid = models.IntegerField(db_column='pID')  # Field name made lowercase.
    url = models.URLField(unique=True)
    date = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'imgur'


class Links(models.Model):
    key = models.TextField()
    url = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'links'


class Settings(models.Model):
    key = models.TextField(unique=True, blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'settings'

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
    admin = models.IntegerField(blank=True, null=True)
    mod_group = models.IntegerField(blank=True, null=True)

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
        db_table = 'wisdom'

    def __str__(self):
        if len(self.text) > 50:
            return '{}...'.format(self.text[:50])
        else:
            return self.text
            

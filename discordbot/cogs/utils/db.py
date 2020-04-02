import logging
from datetime import datetime
from itertools import chain

from django.core.exceptions import FieldError

from discordbot.models import (DiscordSettings, DiscordUser,
                               create_discord_token)

logger = logging.getLogger("botLogger.db")


def get_nickname_cache():
    """Get nickname dictionary from discord user model"""
    query_set = DiscordUser.objects.values_list('id', 'display_name')
    cached_nicknames = {x[0]: x[1] for x in query_set}
    return cached_nicknames


def update_display_names(servers):
    """Update display names for every user in bot.servers"""
    cache = get_nickname_cache()
    users = {m.id: m for m in list(chain(*[s.members for s in servers]))}

    for discord_id, member in users.items():
        if discord_id not in cache:
            DiscordUser.objects.create(id=discord_id,
                                       display_name=member.display_name,
                                       token=create_discord_token(),
                                       avatar_url=member.avatar_url)
        elif member.display_name != cache[discord_id]:
            (DiscordUser.objects
             .filter(id=discord_id)
             .update(display_name=member.display_name))
        if member.avatar_url:
            (DiscordUser.objects
             .filter(id=discord_id)
             .update(avatar_url=member.avatar_url))
        else:
            DiscordUser.objects.filter(id=discord_id).update(avatar_url=None)

    DiscordSettings.objects \
        .filter(key='cache_update') \
        .update(value=datetime.now())
    logger.info('Discord users table has been updated')


def get_random_entry(model):
    """Get random entry from given model

    Args:
        model (BaseModel): Django model with `pid` field

    Returns:
        random_entry: Random entry from given model with pid=0
    """
    try:
        random_entry = model.objects.filter(pid=0).order_by('?').first()
        model.objects.filter(id=random_entry.id).update(pid=1)
    except AttributeError:
        model.objects.all().update(pid=0)
        random_entry = model.objects.filter(pid=0).order_by('?').first()
        model.objects.filter(id=random_entry.id).update(pid=1)
    except FieldError as ex:
        logger.error(ex)
        return None
    return random_entry

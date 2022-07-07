import logging
from datetime import datetime
from itertools import chain

from discordbot.models import DiscordSettings, DiscordUser

logger = logging.getLogger('discordbot.utils.db')


def get_nickname_cache() -> dict[int, str]:
    """Get nickname dictionary from discord user model"""
    query_set = DiscordUser.objects.values_list('id', 'display_name')
    return {x[0]: x[1] for x in query_set}


def sync_users(servers):
    """Update display names for every user in bot.servers"""
    cache = get_nickname_cache()
    users = {m.id: m for m in list(chain(*[s.members for s in servers]))}

    for discord_id, member in users.items():
        if discord_id not in cache:
            DiscordUser.objects.create(
                id=discord_id,
                display_name=member.display_name,
                avatar_url=member.avatar_url
            )
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
    logger.info('Discord users table synced')

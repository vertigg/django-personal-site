import logging
from datetime import datetime
from itertools import chain

from discordbot.models import DiscordSettings, DiscordUser

logger = logging.getLogger('discordbot.utils.db')


def sync_users(servers):
    """Update display names for every user in bot.servers"""
    cache = DiscordUser.get_cached_nicknames()
    users = {m.id: m for m in list(chain(*[s.members for s in servers]))}

    for discord_id, member in users.items():
        if discord_id not in cache:
            DiscordUser.objects.create(
                id=discord_id,
                display_name=member.display_name,
                avatar_url=member.avatar
            )
        elif member.display_name != cache[discord_id]:
            (DiscordUser.objects
             .filter(id=discord_id)
             .update(display_name=member.display_name))
        if member.avatar:
            (DiscordUser.objects
             .filter(id=discord_id)
             .update(avatar_url=member.avatar))
        else:
            DiscordUser.objects.filter(id=discord_id).update(avatar_url=None)

    DiscordSettings.objects \
        .filter(key='cache_update') \
        .update(value=datetime.now())
    logger.info('Discord users table synced')

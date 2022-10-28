import logging
from datetime import datetime
from itertools import chain

from allauth.socialaccount.models import SocialAccount
from discordbot.models import DiscordSettings, DiscordUser

logger = logging.getLogger('discordbot.utils.db')


def sync_users(servers):
    """Update display names for every user in bot.servers"""
    cache = DiscordUser.get_cached_nicknames()
    users = {m.id: m for m in list(chain(*[s.members for s in servers]))}

    for discord_id, member in users.items():
        if discord_id not in cache:
            new_user = DiscordUser.objects.create(
                id=discord_id,
                display_name=member.display_name,
                avatar_url=member.avatar
            )
            sync_with_social_account(new_user, discord_id)
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


def sync_with_social_account(new_user: DiscordUser, discord_id: int):
    try:
        social_account = SocialAccount.objects.get(uid=discord_id)
        new_user.user = social_account.user
        new_user.save()
    except SocialAccount.DoesNotExist:
        pass

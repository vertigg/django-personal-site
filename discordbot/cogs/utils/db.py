import logging
from datetime import datetime
from itertools import chain

from allauth.socialaccount.models import SocialAccount

from discordbot.models import DiscordSettings, DiscordUser

logger = logging.getLogger('discord.utils.db')


async def sync_users(servers):
    """Update display names for every user in bot.servers"""
    cache = await DiscordUser.get_cached_nicknames()
    users = {m.id: m for m in list(chain(*[s.members for s in servers]))}

    for discord_id, member in users.items():
        if discord_id not in cache:
            new_user = await DiscordUser.objects.acreate(
                id=discord_id,
                display_name=member.display_name,
                avatar_url=member.avatar
            )
            await sync_with_social_account(new_user, discord_id)
        elif member.display_name != cache[discord_id]:
            (await DiscordUser.objects
             .filter(id=discord_id)
             .aupdate(display_name=member.display_name)
             )
        if member.avatar:
            (await DiscordUser.objects
             .filter(id=discord_id)
             .aupdate(avatar_url=member.avatar))
        else:
            await DiscordUser.objects.filter(id=discord_id).aupdate(avatar_url=None)

    await DiscordSettings.objects \
        .filter(key='cache_update') \
        .aupdate(value=datetime.now())
    logger.info('Discord users table synced')


async def sync_with_social_account(new_user: DiscordUser, discord_id: int):
    try:
        social_account = await SocialAccount.objects.select_related('user').aget(uid=discord_id)
        new_user.user = social_account.user
        await new_user.asave()
    except SocialAccount.DoesNotExist:
        pass

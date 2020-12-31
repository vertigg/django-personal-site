import logging
from functools import wraps
from re import match

from django.utils import timezone

from discordbot.models import DiscordUser

logger = logging.getLogger('discordbot.utils.checks')


def check_author_name(discord_id, cache):
    return cache[discord_id] if discord_id in cache else discord_id


def is_image_mimetype(content_type):
    return content_type in ("image/png", "image/jpeg", "image/jpg")


def is_youtube_link(url):
    """Checks if url is youtube-like"""
    pattern = r'http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?'
    return bool(match(pattern, url))


def admin_command(func):
    """Checks if command executed by admin or bot's owner"""
    @wraps(func)
    async def decorated(self, ctx, **kwargs):
        if DiscordUser.is_admin(ctx.message.author.id):
            return await func(self, ctx, **kwargs)
        return await ctx.send(
            f"You don't have permissions to call `{ctx.command.name}` command")
    return decorated


def mod_command(func):
    """Checks if command executed by mod"""
    @wraps(func)
    async def decorated(self, ctx, **kwargs):
        if DiscordUser.is_moderator(ctx.message.author.id):
            return await func(self, ctx, **kwargs)
        return await ctx.send(
            f"You don't have permissions to call `{ctx.command.name}` command")
    return decorated

import logging
from functools import wraps
from re import match
from types import FunctionType

from discord.enums import ChannelType
from discord.interactions import Interaction
from discordbot.models import DiscordUser

logger = logging.getLogger('discordbot.utils.checks')
IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg"}


def is_image_mimetype(content_type: str) -> bool:
    return content_type in IMAGE_TYPES


def is_youtube_link(url: str) -> bool:
    """Checks if url is youtube-like"""
    pattern = r'http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?'
    return bool(match(pattern, url))


async def send_warning_message(context, message):
    if isinstance(context, Interaction):
        return await context.response.send_message(message, ephemeral=True)
    return await context.send(message)


def admin_command(func: FunctionType) -> FunctionType:
    """Checks if command executed by admin or bot's owner"""
    @wraps(func)
    async def decorated(self, ctx, *args, **kwargs):
        user_id = ctx.user.id if isinstance(ctx, Interaction) else ctx.message.author.id
        if DiscordUser.is_admin(user_id):
            return await func(self, ctx, *args, **kwargs)
        return await send_warning_message(
            ctx, f"You don't have permissions to call `{ctx.command.name}` command"
        )
    return decorated


def mod_command(func: FunctionType) -> FunctionType:
    """Checks if command executed by mod"""
    @wraps(func)
    async def decorated(self, ctx, *args, **kwargs):
        user_id = ctx.user.id if isinstance(ctx, Interaction) else ctx.message.author.id
        if DiscordUser.is_moderator(user_id):
            return await func(self, ctx, *args, **kwargs)
        return await send_warning_message(
            ctx, f"You don't have permissions to call `{ctx.command.name}` command"
        )
    return decorated


def text_channels_only(func: FunctionType) -> FunctionType:
    """Prevents using command outside text channels"""
    @wraps(func)
    async def decorated(self, ctx, *args, **kwargs):
        if ctx.channel and ctx.channel.type == ChannelType.text:
            return await func(self, ctx, *args, **kwargs)
        return await ctx.send("You can't use this command here")
    return decorated

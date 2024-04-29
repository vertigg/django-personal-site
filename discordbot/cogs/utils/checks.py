import logging
import re
from functools import wraps
from types import FunctionType

from discord.enums import ChannelType
from discord.interactions import Interaction

from discordbot.cogs.utils.exceptions import (
    DuplicatedProfileException, PrivateProfileException
)
from discordbot.cogs.utils.formatters import send_error_embed
from discordbot.cogs.utils.http import async_httpx_request
from discordbot.config import settings
from discordbot.models import DiscordUser

logger = logging.getLogger('discord.utils.checks')

POE_PROFILE_URL = 'https://pathofexile.com/character-window/get-characters?accountName={}'
YT_LINK_PATTERN = re.compile(r'http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?[\w\?=]*)?')


def is_allowed_image_mimetype(content_type: str) -> bool:
    return content_type in settings.ALLOWED_IMAGE_TYPES


def is_youtube_link(url: str) -> bool:
    """Checks if url is youtube-like"""
    return bool(YT_LINK_PATTERN.match(url))


def admin_command(func: FunctionType) -> FunctionType:
    """Checks if command executed by admin or bot's owner"""
    @wraps(func)
    async def decorated(self, ctx, *args, **kwargs):
        user_id = ctx.user.id if isinstance(ctx, Interaction) else ctx.message.author.id
        if await DiscordUser.is_admin(user_id):
            return await func(self, ctx, *args, **kwargs)
        return await send_error_embed(
            ctx, f"You don't have permissions to call `{ctx.command.name}` command"
        )
    return decorated


def mod_command(func: FunctionType) -> FunctionType:
    """Checks if command executed by mod"""
    @wraps(func)
    async def decorated(self, ctx, *args, **kwargs):
        user_id = ctx.user.id if isinstance(ctx, Interaction) else ctx.message.author.id
        if await DiscordUser.is_moderator(user_id):
            return await func(self, ctx, *args, **kwargs)
        return await send_error_embed(
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


async def validate_poe_profile(profile_name: str) -> str | None:
    if not profile_name:
        return None
    if await DiscordUser.objects.filter(poe_profile=profile_name).aexists():
        raise DuplicatedProfileException('Account is already in the system')
    response, exc = await async_httpx_request("OPTIONS", POE_PROFILE_URL.format(profile_name))
    if exc:
        logger.error(exc)
    if exc or response.is_error:
        raise PrivateProfileException(f'"{profile_name}" account is private or does not exist')
    return response

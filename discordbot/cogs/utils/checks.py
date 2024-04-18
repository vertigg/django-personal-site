import logging
from functools import wraps
from re import match
from types import FunctionType

import aiohttp
from discord.enums import ChannelType
from discord.interactions import Interaction

from discordbot.cogs.utils.exceptions import (
    DuplicatedProfileException, PrivateProfileException
)
from discordbot.models import DiscordUser

logger = logging.getLogger('discord.utils.checks')

IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg"}  # image/webp is not supported by imgur
POE_PROFILE_URL = 'https://pathofexile.com/character-window/get-characters?accountName={}'
DEFAULT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
    )
}


def is_allowed_image_mimetype(content_type: str) -> bool:
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
        if await DiscordUser.is_admin(user_id):
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
        if await DiscordUser.is_moderator(user_id):
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


async def validate_poe_profile(profile_name: str) -> str | None:
    if not profile_name:
        return None
    if await DiscordUser.objects.filter(poe_profile=profile_name).aexists():
        raise DuplicatedProfileException('Account is already in the system')

    async with aiohttp.ClientSession(headers=DEFAULT_HEADERS) as client:
        response = await client.options(POE_PROFILE_URL.format(profile_name))
        if response.status != 200:
            raise PrivateProfileException(f'"{profile_name}" account is private or does not exist')

    return profile_name

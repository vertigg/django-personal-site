"""COG FOR ADMIN COMMANDS"""

import inspect
import logging
import os
import random
import sys
import itertools

import aiohttp
import pandas as pd
from discord import VoiceRegion as region
from discord.errors import Forbidden
from discord.ext import commands
from discord.ext.commands.context import Context
from discordbot.cogs.utils.checks import admin_command, mod_command

logger = logging.getLogger('discordbot.admin')


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.eu_regions = [
            region.amsterdam,
            region.eu_central,
            region.frankfurt,
            region.eu_west,
        ]

    @commands.command(hidden=True)
    @mod_command
    async def region(self, ctx: Context):
        new_region = random.choice(
            [x for x in self.eu_regions if x != ctx.guild.region])
        try:
            await ctx.guild.edit(region=new_region, reason="Lag Change")
            await ctx.send(f'Changed to {new_region} region', delete_after=5)
        except Forbidden:
            await ctx.send(f'Missing permissions for editing {ctx.guild}')

    @commands.command(hidden=True)
    @admin_command
    async def change_avatar(self, ctx: Context, url: str):
        """Sets Bot's avatar"""
        try:
            async with aiohttp.ClientSession(loop=self.bot.loop) as client:
                response = await client.get(url)
                data = await response.read()
            await self.bot.user.edit(avatar=data)
            await ctx.send("New avatar has been set", delete_after=5)
        except Exception as exc:
            await ctx.send("Can't change avatar now. Whoops I guess")
            logger.exception(exc)

    @commands.command(hidden=True)
    @admin_command
    async def change_nickname(self, ctx: Context, nickname: str):
        """Sets Bot's nickname"""
        try:
            await self.bot.user.edit(username=nickname)
            await ctx.send("Done.", delete_after=5)
            logger.debug("changed nickname")
        except Exception as exc:
            await ctx.send("Error, check your console or logs for more information.")
            logger.exception(exc)

    @commands.command(hidden=True)
    @admin_command
    async def load(self, ctx: Context, extension_name: str):
        """Loads an extension."""
        try:
            if "cogs." not in extension_name:
                extension_name = "cogs." + extension_name
            self.bot.load_extension(extension_name)
        except (AttributeError, ImportError) as ex:
            await ctx.send("```py\n{}: {}\n```".format(type(ex).__name__, str(ex)))
            return
        await ctx.send(f"{extension_name} loaded.")

    @commands.command(hidden=True)
    @admin_command
    async def unload(self, ctx: Context, extension_name: str):
        """Unloads an extension."""
        if "cogs." not in extension_name:
            extension_name = "cogs." + extension_name
        self.bot.unload_extension(extension_name)
        await ctx.send(f"{extension_name} unloaded.")

    @commands.command(hidden=True)
    @admin_command
    async def debug(self, ctx: Context, *, code: str):
        """Evaluates code."""
        code = code.strip('` `')
        python = '```py\n{}\n```'
        try:
            result = eval(code)
            if inspect.isawaitable(result):
                result = await result
        except Exception as ex:
            await ctx.send(python.format(type(ex).__name__ + ': ' + str(ex)))
            result = None
            return
        await ctx.send(python.format(result))

    @commands.command(hidden=True)
    @admin_command
    async def gitupdate(self, _):
        """Autoupdate bot to latest commit"""
        os.system('git pull')
        os.system('supervisorctl restart bot')


def setup(bot):
    bot.add_cog(Admin(bot))

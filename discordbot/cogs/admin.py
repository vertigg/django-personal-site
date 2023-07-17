"""COG FOR ADMIN COMMANDS"""

import asyncio
import inspect
import itertools
import logging
import os
import random
import sys

import aiohttp
import pandas as pd
import requests
from celery import states
from discord.ext import commands
from discord.ext.commands.context import Context
from discordbot.cogs.utils.checks import admin_command, mod_command
from discordbot.cogs.utils.db import sync_users
from poe.tasks import LadderUpdateTask

logger = logging.getLogger('discord.admin')


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(hidden=True)
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

    @commands.is_owner()
    @commands.command(hidden=True)
    async def change_nickname(self, ctx: Context, nickname: str):
        """Sets Bot's nickname"""
        try:
            await self.bot.user.edit(username=nickname)
            await ctx.send("Done.", delete_after=5)
            logger.debug("changed nickname")
        except Exception as exc:
            await ctx.send("Error, check your console or logs for more information.")
            logger.exception(exc)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def load(self, ctx: Context, extension_name: str):
        """Loads an extension."""
        try:
            if "cogs." not in extension_name:
                extension_name = "discordbot.cogs." + extension_name
            await self.bot.load_extension(extension_name)
        except (AttributeError, ImportError) as ex:
            await ctx.send("```py\n{}: {}\n```".format(type(ex).__name__, str(ex)))
            return
        await ctx.send(f"{extension_name} loaded.")

    @commands.is_owner()
    @commands.command(hidden=True)
    async def unload(self, ctx: Context, extension_name: str):
        """Unloads an extension."""
        if "cogs." not in extension_name:
            extension_name = "discordbot.cogs." + extension_name
        await self.bot.unload_extension(extension_name)
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
    async def update_users(self, ctx):
        """Force update display names for every user in bot.servers"""
        try:
            await sync_users(self.bot.guilds)
        except Exception as exc:
            await ctx.send(exc)

    @commands.command(hidden=True)
    @mod_command
    async def ladder_update(self, ctx):
        result = LadderUpdateTask.delay()
        await ctx.send("`Updating ladder...`", delete_after=30)
        logger.info('[LADDER]: Ladder Update has been started')
        while result.state == states.PENDING:
            await ctx.trigger_typing()
            await asyncio.sleep(10)
        if result.state == states.SUCCESS:
            await ctx.send('Ladder has been updated', delete_after=30)
        else:
            await ctx.send('Error during ladder update operation')


async def setup(bot):
    await bot.add_cog(Admin(bot))

import asyncio
import logging

from celery import states
from discord.ext import commands
from poeladder.tasks import LadderUpdateTask

from .utils.checks import admin_command, mod_command
from .utils.db import sync_users

logger = logging.getLogger('discordbot.django')


class DjangoDiscord(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.process = None
        self.lock = False

    @commands.command(hidden=True)
    @admin_command
    async def update_users(self, ctx):
        """Force update display names for every user in bot.servers"""
        try:
            sync_users(self.bot.guilds)
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


def setup(bot):
    bot.add_cog(DjangoDiscord(bot))

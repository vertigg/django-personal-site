import asyncio
import logging
import subprocess
import sys

from discord.ext import commands

from discordbot.models import DiscordUser

from .utils.checks import admin_command, mod_command
from .utils.db import update_display_names

logger = logging.getLogger('discordbot.django')


class DjangoDiscord(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.process = None
        self.lock = False

    @commands.command()
    async def register(self, ctx):
        """
        Command that creates activation link for current DiscordUser. User will be
        created if it doesn't exist in database. If user exists, this will
        regenerate token
        """
        discord_user = DiscordUser.objects.filter(id=ctx.message.author.id).first()
        if not discord_user:
            discord_user = DiscordUser.objects.create(
                id=ctx.message.author.id,
                display_name=ctx.message.author.display_name,
                avatar_url=ctx.message.author.avatar_url
            )
        url = discord_user.get_activation_url()
        message = ('Registration complete. You can finish user profile creation '
                   f'by following this url: {url}. If link does not work for '
                   'some reason you can always finish registration manually by '
                   f'typing token below into token form ```{discord_user.token}```')
        await ctx.author.send(message)

    @commands.command(hidden=True)
    @admin_command
    async def users_update(self, ctx):
        """Force update display names for every user in bot.servers"""
        try:
            update_display_names(self.bot.guilds)
        except Exception as ex:
            await ctx.send(ex)

    @commands.command(hidden=True)
    @mod_command
    async def ladder_update(self, ctx):
        if not self.lock:
            try:
                self.lock = True
                logger.info('[LADDER]: Ladder Update has been started')
                await ctx.send("`Updating ladder...`", delete_after=30)
                self.process = subprocess.Popen(
                    [sys.executable, "manage.py", "ladder_update"],
                    stderr=subprocess.PIPE)
                while self.process.poll() is None:
                    await ctx.trigger_typing()
                    await asyncio.sleep(10)
                if self.process.poll() is 0:
                    await ctx.send('Ladder has been updated', delete_after=30)
                    logger.info('[LADDER]: Finished updating')
                else:
                    await ctx.send('Le error')
            except Exception as exc:
                logger.error(exc)
                await ctx.send(exc)
            finally:
                self.lock = False


def setup(bot):
    bot.add_cog(DjangoDiscord(bot))

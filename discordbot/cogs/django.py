import asyncio
import logging
import subprocess

from discord.ext import commands

from discordbot.models import DiscordUser, create_discord_token

from .utils.checks import admin_command, mod_command
from .utils.db import update_display_names

logger = logging.getLogger('botLogger.django')


class DjangoDiscord(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.process = None
        self.lock = False

    @commands.command()
    async def register(self, ctx):
        """Get your website token!"""
        token = self.generate_token(ctx.message.author.id)
        await ctx.author.send(token)

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
                    ["python", "manage.py", "ladder_update"], stderr=subprocess.PIPE)
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

    @staticmethod
    def generate_token(discord_id: str):
        """Generate token for registration"""
        new_token = create_discord_token()
        DiscordUser.objects.filter(id=discord_id).update(token=new_token)
        return new_token


def setup(bot):
    bot.add_cog(DjangoDiscord(bot))

import asyncio
import logging
import sys
from subprocess import PIPE, Popen

from discord.ext import commands

from discordbot.models import DiscordLink

logger = logging.getLogger('discordbot.kf')


class KillingFloor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = False

    @commands.group(pass_context=True)
    async def kf(self, ctx):
        """KF2 Achievements spreadsheet"""
        if not ctx.invoked_subcommand:
            await ctx.send(DiscordLink.get('kf2'))

    @kf.command()
    async def update(self, ctx):
        """Update KF2 Achievements spreadsheet"""
        if self.lock:
            return
        try:
            self.lock = True
            logger.info('[KFGOOGLE]: Script started')

            with Popen([sys.executable, "discordbot/SteamStats.py"], stderr=PIPE) as process:
                while process.poll() is None:
                    await asyncio.sleep(1)
                if process.poll() is 0:
                    await ctx.send("`Таблицы ачивок обновлены`")
                    logger.info('[KFGOOGLE]: Script finished')
                else:
                    await ctx.send("`There were some errors during update. Check logs for more info`")
                    logger.error(
                        "[KFGOOGLE]: There were some errors during update. Check logs for more info")
        finally:
            self.lock = False


def setup(bot):
    bot.add_cog(KillingFloor(bot))

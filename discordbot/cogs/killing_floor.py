import asyncio
import logging
import subprocess

from discord.ext import commands

from discordbot.models import DiscordLink

logger = logging.getLogger("botLogger.kf")


class KillingFloor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = False
        self.process = None

    def cog_unload(self):
        if self.process:
            self.process.kill()
            self.lock = False

    @commands.group(pass_context=True)
    async def kf(self, ctx):
        """KF2 Achievements spreadsheet"""
        if not ctx.invoked_subcommand:
            await ctx.send(DiscordLink.objects.get(key='kf2'))

    @kf.command()
    async def update(self, ctx):
        """Update KF2 Achievements spreadsheet"""
        if not self.lock:
            self.lock = True
            logger.info('[KFGOOGLE]: Script started')
            self.process = subprocess.Popen(
                ["python3", "discordbot/SteamStats.py"], stderr=subprocess.PIPE)
            while self.process.poll() is None:
                await asyncio.sleep(1)
            if self.process.poll() is 0:
                await ctx.send("`Таблицы ачивок обновлены`")
                logger.info('[KFGOOGLE]: Script finished')
            else:
                await ctx.send("`There were some errors during update. Check logs for more info`")
                logger.error(
                    "[KFGOOGLE]: There were some errors during update. Check logs for more info")
            self.lock = False


def setup(bot):
    bot.add_cog(KillingFloor(bot))

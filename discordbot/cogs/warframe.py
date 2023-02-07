"""
Cog for checking Warframe alerts
"""

import logging
from functools import reduce
from operator import or_

import discord
from discord.errors import InvalidArgument
from discord.ext import commands, tasks
from discord.utils import get as get_user
from django.conf import settings
from django.db.models import Q

from discordbot.models import DiscordUser, WFAlert, WFSettings

logger = logging.getLogger('discordbot.warframe')


class Warframe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.watchdog = self.warframe_alert_watchdog.start()

    def cog_unload(self):
        self.watchdog.cancel()

    @tasks.loop(seconds=60, reconnect=True)
    async def warframe_alert_watchdog(self):
        for alert in WFAlert.objects.filter(announced=False):
            matches = [key for key, value in WFSettings.alerts.items()
                       if value.lower() in alert.content.lower()]
            if matches:
                filters = reduce(or_, [
                    Q(**{f'wf_settings__{match}': True}) for match in matches
                ])
                for sub in DiscordUser.objects.select_related().filter(filters):
                    try:
                        user = get_user(self.bot.get_all_members(), id=sub.id)
                        if user:
                            await user.send(embed=self.create_embed(alert))
                        else:
                            logger.error(
                                "Can't find %s in get_all_members(). User unsubbed", sub)
                            sub.wf_settings.reset_settings()
                    except InvalidArgument:
                        pass
            alert.announced = True
            alert.save()

    @warframe_alert_watchdog.before_loop
    async def before_task(self):
        await self.bot.wait_until_ready()

    def create_embed(self, alert):
        embed = discord.Embed(
            title="**Warframe Alert**",
            colour=discord.Colour(0xff0074),
            description=f"{alert.content}\n\n[Unsubscribe]({settings.DEFAULT_DOMAIN}/profile)"
        )
        embed.set_thumbnail(url="https://i.imgur.com/ZvDNumd.png")
        embed.set_footer(text=f"WFAlert ID: {alert.id}")
        return embed


def setup(bot):
    bot.add_cog(Warframe(bot))

"""
Cog for checking Warframe alerts
"""

import logging

import discord
from discord.errors import InvalidArgument
from discord.ext import commands, tasks
from discord.utils import get as get_user
from django.db.models import Q

from discordbot.models import DiscordUser, WFAlert, WFSettings

logger = logging.getLogger("botLogger.warframe")


class Warframe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.watchdog = self.warframe_alert_watchdog.start()

    def cog_unload(self):
        self.watchdog.cancel()

    @tasks.loop(seconds=60, reconnect=True)
    async def warframe_alert_watchdog(self):
        new_alerts = WFAlert.objects.filter(announced=False)
        for alert in new_alerts:
            matches = [key for key, value in WFSettings.alerts.items()
                       if value.lower() in alert.content.lower()]
            if matches:
                if len(matches) == 2:
                    subscribers = DiscordUser.objects.select_related().filter(
                        Q(**{f'wf_settings__{matches[0]}': True}) |
                        Q(**{f'wf_settings__{matches[1]}': True}))
                else:
                    subscribers = DiscordUser.objects.select_related().filter(
                        **{f'wf_settings__{matches[0]}': True})
                for sub in subscribers:
                    try:
                        user = get_user(
                            self.bot.get_all_members(), id=sub.id)
                        if user:
                            await user.send(embed=self.create_embed(alert))
                        else:
                            logger.error(
                                "Can't find %s in get_all_members(). User unsubbed", sub)
                            self._unsub_user(sub)
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
            description=f"{alert.content}\n\n[Unsubscribe](https://epicvertigo.xyz/profile)")
        embed.set_thumbnail(url="https://i.imgur.com/ZvDNumd.png")
        embed.set_footer(text=f"WFAlert ID: {alert.id}")
        return embed

    def _unsub_user(self, user):
        """Set's user settings to Default"""
        settings = user.wf_settings
        fields = [x.name for x in settings._meta.fields if x.name != 'id']
        for field in fields:
            setattr(settings, field, False)
        settings.save()


def setup(bot):
    bot.add_cog(Warframe(bot))

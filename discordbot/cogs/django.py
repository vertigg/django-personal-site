import logging

from discord.ext import commands

from discordbot.models import DiscordUser, create_discord_token
from .utils.checks import admin_command
from .utils.db import update_display_names

logger = logging.getLogger('botLogger.django')


class DjangoDiscord(object):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def register(self, ctx):
        """Get your website token!"""
        token = self.generate_token(ctx.message.author.id)
        await self.bot.send_message(ctx.message.author, token)

    @commands.command(pass_context=True, hidden=True)
    @admin_command
    async def users_update(self, ctx):
        """Force update display names for every user in bot.servers"""
        try:
            update_display_names(self.bot.servers)
        except Exception as ex:
            self.bot.say(ex)

    @staticmethod
    def generate_token(discord_id: str):
        """Generate token for registration"""
        new_token = create_discord_token()
        DiscordUser.objects.filter(id=discord_id).update(token=new_token)
        return new_token


def setup(bot):
    bot.add_cog(DjangoDiscord(bot))

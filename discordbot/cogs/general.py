import logging
import random

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.interactions import Interaction

from discordbot.models import DiscordLink, DiscordSettings

from .utils.checks import admin_command
from .utils.db import sync_users

logger = logging.getLogger('discord.general')


class General(commands.Cog):
    _help_embed: discord.Embed = None

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.update_cache_task = self.update_cache.start()  # pylint: disable=maybe-no-member

    async def cog_unload(self):
        self.update_cache_task.cancel()

    @property
    def help_embed(self):
        if not self._help_embed:
            embed = discord.Embed(title="Tony Bot Help")
            embed.set_thumbnail(url="https://i.imgur.com/rHoLgGu.png")
            embed.add_field(
                name="How to add new mix (image) examples:",
                inline=False,
                value=(
                    "\n`!mix add <URL>`\n`!mix add <URL1> <URL2>`\n`!mix add` + any "
                    "picture attachments\n(combination of urls + attachments also works)"
                )
            )
            embed.add_field(name="How to add new wisdom (text):", inline=False, value="\n`/wisdom add <text>`")
            self._help_embed = embed
        return self._help_embed

    @tasks.loop(hours=24, reconnect=True)
    async def update_cache(self):
        await self.bot.wait_until_ready()
        logger.info('Syncing Discord user with Django database')
        await sync_users(self.bot.guilds)

    @app_commands.command(name='avatar', description="Shows mentioned user's avatar")
    async def avatar(self, interaction: Interaction, user: discord.User):
        await interaction.response.send_message(user.avatar.url)

    @app_commands.command(name='game', description='Change bots current game status')
    @admin_command
    async def game(self, interaction: Interaction, name: str):
        """Change bot's status"""
        await DiscordSettings.aset('game', name)
        await self.bot.change_presence(activity=discord.Game(name=name))
        await interaction.response.send_message('Status changed', ephemeral=True)

    @commands.hybrid_command(name='low')
    async def low(self, ctx: commands.Context) -> None:
        await ctx.send(await DiscordLink.aget('low'))

    @app_commands.command(name='choose', description='Chooses between multiple items')
    async def choose(self, interaction: Interaction, item_1: str, item_2: str):
        await interaction.response.send_message(random.choice([item_1, item_2]))

    @app_commands.command(name='friday', description="It's morbin time")
    async def friday(self, interaction: Interaction):
        await interaction.response.send_message(await DiscordLink.aget('friday'))

    @app_commands.command(name='roll', description='Rolls a number in 1-100 range')
    async def roll(self, interaction: Interaction):
        await interaction.response.send_message(random.randint(1, 101))

    @commands.command(hidden=True)
    async def vb(self, ctx):
        await ctx.send(await DiscordLink.aget('vb', "Can't find saved link for that command"))

    @app_commands.command(name="help", description="Lil' help")
    async def help(self, interaction: Interaction):
        await interaction.response.send_message(embed=self.help_embed)


async def setup(bot):
    await bot.add_cog(General(bot))

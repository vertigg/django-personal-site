import logging
import random

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.interactions import Interaction

from discordbot.models import DiscordLink, DiscordSettings, Gachi

from .utils.checks import admin_command, is_youtube_link, mod_command
from .utils.db import sync_users

logger = logging.getLogger('discordbot.general')


class General(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.update_cache_task = self.update_cache.start()

    def cog_unload(self):
        self.update_cache_task.cancel()

    @tasks.loop(hours=24, reconnect=True)
    async def update_cache(self):
        await self.bot.wait_until_ready()
        logger.info('Syncing Discord user with Django database')
        sync_users(self.bot.guilds)

    @app_commands.command(name='avatar', description="Shows mentioned user's avatar")
    async def avatar(self, interaction: Interaction, user: discord.User):
        await interaction.response.send_message(user.avatar.url)

    @app_commands.command(name='game', description='Change bots current game status')
    @admin_command
    async def game(self, interaction: Interaction, name: str):
        """Change bot's status"""
        DiscordSettings.set('game', name)
        await self.bot.change_presence(activity=discord.Game(name=name))
        await interaction.response.send_message('Status changed', ephemeral=True)

    @commands.hybrid_command(name='low')
    async def low(self, ctx: commands.Context) -> None:
        await ctx.send(DiscordLink.get('low'))

    @app_commands.command(name='choose', description='Chooses between multiple items')
    async def choose(self, interaction: Interaction, item_1: str, item_2: str):
        await interaction.response.send_message(random.choice([item_1, item_2]))

    @app_commands.command(name='friday', description="It's morbin time")
    async def friday(self, interaction: Interaction):
        await interaction.response.send_message(DiscordLink.get('friday'))

    @app_commands.command(name='roll', description='Rolls a number in 1-100 range')
    async def roll(self, interaction: Interaction):
        await interaction.response.send_message(random.randint(1, 101))

    @commands.command(hidden=True)
    async def vb(self, ctx):
        await ctx.send(DiscordLink.get('vb', "Can't find saved link for that command"))

    @commands.group(invoke_without_command=True)
    async def gachi(self, ctx):
        """Take it boy"""
        gachi_obj = Gachi.objects.get_random_entry()
        if gachi_obj is not None:
            await ctx.send(gachi_obj)

    @gachi.command()
    @mod_command
    async def add(self, ctx, url: str):
        if not is_youtube_link(url):
            return await ctx.send('Wrong youtube link format')
        Gachi.objects.create(url=url)
        await ctx.send(f'{url} has been added')


async def setup(bot):
    await bot.add_cog(General(bot))

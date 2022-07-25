import logging
import random
from datetime import datetime

import discord
from discord.ext import commands, tasks
from discordbot.models import DiscordLink, DiscordSettings, Gachi

from .utils.checks import admin_command, is_youtube_link, mod_command
from .utils.db import sync_users
from .utils.formatters import ru_plural

logger = logging.getLogger('discordbot.general')


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.update_cache_task = self.update_cache.start()

    def cog_unload(self):
        self.update_cache_task.cancel()

    @tasks.loop(hours=24, reconnect=True)
    async def update_cache(self):
        await self.bot.wait_until_ready()
        logger.info('Syncing Discord user with Django database')
        sync_users(self.bot.guilds)

    @commands.command()
    async def avatar(self, ctx):
        """Shows user's avatar or avatars of all mentioned users"""
        users = ctx.message.mentions if ctx.message.mentions else [ctx.message.author]
        await ctx.send('\n'.join([str(x.avatar_url) for x in users]))

    @commands.command()
    @admin_command
    async def game(self, ctx, *, name: str = None):
        """Change bot's status"""
        if not name:
            await ctx.send('How to use: `!game "Name"`', delete_after=10)
            return
        DiscordSettings.objects.filter(key='game').update(value=name)
        await self.bot.change_presence(activity=discord.Game(name=name))
        await ctx.send('Status changed', delete_after=15)

    @commands.command(hidden=True)
    async def low(self, ctx):
        await ctx.send(DiscordLink.get('low'))

    @commands.command()
    async def choose(self, ctx, *choices: str):
        """Chooses between two items"""
        await ctx.send(random.choice(choices))

    @commands.command(hidden=True)
    async def friday(self, ctx):
        await ctx.send(DiscordLink.get('friday'))

    @commands.command()
    async def roll(self, ctx):
        """Rolls from 1 to 100"""
        await ctx.send(random.randint(1, 101))

    @commands.command(hidden=True)
    async def vb(self, ctx):
        await ctx.send(DiscordLink.get('vb'))

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
            await ctx.send('Wrong youtube link format')
            return
        Gachi.objects.create(url=url)
        await ctx.send(f'{url} has been added')

    @commands.command(aliases=['perediwka'])
    async def peredishka(self, ctx):
        if ctx.message.author.id in [138275152415817728]:
            await ctx.send('Передышки не будет')
            return
        current_weekday = datetime.now().weekday()
        if current_weekday in [5, 6]:
            await ctx.send('Ахаха передишка')
            return
        difference = 5 - current_weekday
        await ctx.send(
            f'Осталось {difference} '
            f'{ru_plural(difference, ["день", "дня", "дней"])} до передишки'
        )


def setup(bot):
    bot.add_cog(General(bot))

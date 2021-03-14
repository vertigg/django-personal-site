import logging
import random
import re
from datetime import datetime

import discord
from discord.ext import commands, tasks
from discordbot.models import DiscordLink, DiscordSettings, DiscordUser, Gachi

from .utils.checks import admin_command, is_youtube_link, mod_command
from .utils.db import update_display_names
from .utils.formatters import ru_plural

logger = logging.getLogger('discordbot.general')


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.mention_pattern = re.compile(r'\<\@\!?(?P<id>\d+)\>')
        self.update_cache_task = self.update_cache.start()

    def cog_unload(self):
        self.update_cache_task.cancel()

    @tasks.loop(hours=24, reconnect=True)
    async def update_cache(self):
        await self.bot.wait_until_ready()
        logger.info('Syncing Discord user with Django database')
        update_display_names(self.bot.guilds)

    @commands.command()
    async def avatar(self, ctx, mention=None):
        """Shows user's avatar"""
        if not mention:
            await ctx.send(ctx.message.author.avatar_url)
        else:
            match = self.mention_pattern.match(mention)
            if not match:
                await ctx.send('```How to use - !avatar @User```')
            else:
                discord_id = match.group(1)
                try:
                    avatar = DiscordUser.objects.get(id=discord_id).avatar_url
                    await ctx.send(avatar)
                except DiscordUser.DoesNotExist:
                    await ctx.send("```Can't find discord user```")
                    # Trigger sync update
                    update_display_names(self.bot.guilds)

    @commands.command()
    @admin_command
    async def game(self, ctx, *args):
        """Change bot's status"""
        game = ' '.join(args)
        if not game:
            await ctx.send('How to use: `!game "Name"`')
        else:
            DiscordSettings.objects.filter(key='game').update(value=game)
            await self.bot.change_presence(activity=discord.Game(name=game))
            await ctx.send('Status changed', delete_after=15)

    @commands.command(hidden=True)
    async def shles(self, ctx):
        """SHLES"""
        await ctx.send(DiscordLink.get('shles'))

    @commands.command(hidden=True)
    async def low(self, ctx):
        if ctx.message.author.id == 127135903125733376:
            await ctx.send(DiscordLink.get('low'))
        else:
            await ctx.send('<:bearrion:230370930600312832>')

    @commands.command()
    async def cytube(self, ctx):
        """Для тех кто не умеет добавлять сайты в закладки"""
        cytube_url = DiscordLink.get('cytube')
        movies_url = DiscordLink.get('movies')
        await ctx.send(
            f'`Смотреть` <:bearrion:230370930600312832> {cytube_url}\n'
            f'`Брать кинцо` <:cruzhulk:230370931065749514> {movies_url}'
        )

    @commands.command()
    async def free(self, ctx):
        """Holy scriptures"""
        await ctx.send(f'`Живи молодым и умри молодым` {DiscordLink.get("free")}')

    @commands.command()
    async def choose(self, ctx, *choices: str):
        """Chooses between two items"""
        await ctx.send(random.choice(choices))

    @commands.command(hidden=True)
    async def friday(self, ctx):
        await ctx.send(DiscordLink.get('friday'))

    @commands.command(hidden=True)
    async def flick(self, ctx):
        await ctx.send(DiscordLink.get('ricardo'))

    @commands.command()
    async def roll(self, ctx):
        """Rolls from 1 to 100"""
        await ctx.send(random.randint(1, 101))

    @commands.command(hidden=True)
    async def firstrule(self, ctx):
        await ctx.send('Never hook first <:smart:282452131552690176>')

    @commands.command(hidden=True)
    async def secondrule(self, ctx):
        await ctx.send("You can't counter Pharah <:Kappa:230228691945390080>")

    @commands.command(hidden=True)
    async def thirdrule(self, ctx):
        await ctx.send("Ко мне говно <:4Head:230227653783846912>")

    @commands.command(hidden=True)
    async def vb(self, ctx):
        await ctx.send(DiscordLink.get('vb'))

    @commands.group()
    async def gachi(self, ctx):
        """Take it boy"""
        if not ctx.invoked_subcommand:
            gachi_obj = Gachi.objects.get_random_entry()
            if gachi_obj is not None:
                await ctx.send(gachi_obj)

    @gachi.command()
    @mod_command
    async def add(self, ctx, url: str):
        if is_youtube_link(url):
            Gachi.objects.create(url=url)
            await ctx.send('{} added'.format(url))
        else:
            await ctx.send('Wrong youtube link format')

    @commands.command(aliases=['perediwka'])
    async def peredishka(self, ctx):
        if ctx.message.author.id in [138275152415817728]:
            await ctx.send('Передышки не будет')
        else:
            current_weekday = datetime.now().weekday()
            if current_weekday not in [5, 6]:
                difference = 5 - current_weekday
                await ctx.send(f'Осталось {difference} '
                               f'{ru_plural(difference, ["день", "дня", "дней"])} до передишки')
            else:
                await ctx.send('Ахаха передишка')


def setup(bot):
    bot.add_cog(General(bot))

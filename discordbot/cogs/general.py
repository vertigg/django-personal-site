import logging
import random
import re
from datetime import datetime

import discord
import pandas as pd
import pytz
from discord.ext import commands
from discord.errors import HTTPException
from markovify import Text

from discordbot.models import (DiscordLink, DiscordSettings, DiscordUser,
                               Gachi, MarkovText)

from .utils.checks import admin_command, is_youtube_link, mod_command
from .utils.db import get_random_entry, update_display_names
from .utils.formatters import clean_up_markov_text, ru_plural


logger = logging.getLogger('botLogger.general')


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.markov_model = MarkovText.objects.first()
        self.markov_text = Text(self.markov_model.text)

    @staticmethod
    def get_link(key):
        """Helper method that returns DiscordLink object by given key"""
        return DiscordLink.objects.get(key=key)

    @commands.command()
    async def avatar(self, ctx, mention=None):
        """Shows user's avatar"""
        mention_pattern = r"\<\@\!?(?P<id>\d+)\>"
        if not mention:
            await ctx.send(ctx.message.author.avatar_url)
            return
        if mention:
            match = re.match(mention_pattern, mention)
            if not match:
                await ctx.send('```How to use - !avatar @User```')
                return
            else:
                discord_id = match.group(1)
                try:
                    avatar = DiscordUser.objects.get(id=discord_id).avatar_url
                    await ctx.send(avatar)
                except DiscordUser.DoesNotExist:
                    await ctx.send("```Can't find discord user```")
                    update_display_names(self.bot.servers)

    @commands.command()
    @mod_command
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
        await ctx.send(self.get_link('shles'))

    @commands.command()
    async def ip(self, ctx):
        """Напомните ип плс"""
        await ctx.send(str(DiscordSettings.objects.get(key='ip')) + ' <:OSsloth:230773934197440522>')

    @commands.command(hidden=True)
    async def low(self, ctx):
        if ctx.message.author.id == 127135903125733376:
            await ctx.send(self.get_link('low'))
        else:
            await ctx.send('<:bearrion:230370930600312832>')

    @commands.command()
    async def cytube(self, ctx):
        """Для тех кто не умеет добавлять сайты в закладки"""
        cytube_url = self.get_link('cytube')
        movies_url = self.get_link('movies')
        await ctx.send(f'`Смотреть` <:bearrion:230370930600312832> {cytube_url}\n'
                       f'`Брать кинцо` <:cruzhulk:230370931065749514> {movies_url}')

    @commands.command()
    async def free(self, ctx):
        """Holy scriptures"""
        await ctx.send(f'`Живи молодым и умри молодым` {self.get_link("free")}')

    @commands.command()
    async def choose(self, ctx, *choices: str):
        """Chooses between two items"""
        await ctx.send(random.choice(choices))

    @commands.command(hidden=True)
    async def friday(self, ctx):
        await ctx.send(self.get_link('friday'))

    @commands.command(hidden=True)
    async def flick(self, ctx):
        await ctx.send(self.get_link('ricardo'))

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
        await ctx.send(self.get_link('vb'))

    @commands.group()
    async def gachi(self, ctx):
        """Take it boy"""
        if not ctx.invoked_subcommand:
            gachi_obj = get_random_entry(Gachi)
            if gachi_obj is not None:
                await ctx.send(gachi_obj.url)

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
        current_weekday = datetime.now().weekday()
        if current_weekday not in [5, 6]:
            difference = 5 - current_weekday
            await ctx.send(f'Осталось {difference} '
                           f'{ru_plural(difference, ["день", "дня", "дней"])} до передишки')
        else:
            await ctx.send('Ахаха передишка')

    @commands.group(invoke_without_command=True)
    async def markov(self, ctx, *, sentence_size=200):
        if not ctx.invoked_subcommand:
            await ctx.send(self.markov_text.make_short_sentence(sentence_size))

    @markov.command()
    @admin_command
    async def update(self, ctx):
        if ctx.guild.id in [178976406288465920, 121372102522699778]:
            self.markov_model.refresh_from_db()
            if self.markov_model.last_update:
                last_update = self.markov_model.last_update.replace(tzinfo=None)
                logger.info(f'Updating markov text since {last_update}')
                messages = await ctx.channel.history(limit=None, after=last_update).flatten()
            else:
                logger.info('Downloading chat history')
                messages = await ctx.channel.history(limit=None).flatten()
            if messages:
                messages_df = pd.DataFrame([{
                    'message_id': x.id,
                    'author_id': x.author.id,
                    'content': x.content,
                    'created_at': x.created_at,
                } for x in messages]).astype({'created_at': 'datetime64'})
                new_text = clean_up_markov_text(messages_df)
                if new_text:
                    self.markov_model.text = f'{new_text} {self.markov_model.text}'
                    self.markov_model.last_update = (messages_df.created_at
                                                     .dt.tz_localize(pytz.UTC)
                                                     .dt.to_pydatetime().max())
                    self.markov_model.save()
                    self.markov_text = Text(self.markov_model.text)
                    logger.info(f'Markov text has been updated with {len(new_text)} characters')
                else:
                    logger.info('There are no messages to add')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(error, 'original') and isinstance(error.original, HTTPException):
            if ctx.command.name == 'markov':
                await ctx.send(f"Can't generate text with length of {ctx.kwargs.get('sentence_size')}")


def setup(bot):
    bot.add_cog(General(bot))

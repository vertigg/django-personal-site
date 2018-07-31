import random
import re

import discord
from discord.ext import commands

from discordbot.models import DiscordLink, DiscordSettings, DiscordUser, Gachi
from .utils.checks import admin_command, mod_command
from .utils.db import get_random_entry, update_display_names


class General(object):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def avatar(self, ctx, mention=None):
        """Shows user's avatar"""
        mention_pattern = r"\<\@\!?(?P<id>\d+)\>"
        if not mention:
            await self.bot.say(ctx.message.author.avatar_url)
            return
        if mention:
            match = re.match(mention_pattern, mention)
            if not match:
                await self.bot.say('```How to use - !avatar @User```')
                return
            else:
                discord_id = match.group(1)
                try:
                    avatar = DiscordUser.objects.get(id=discord_id).avatar_url
                    await self.bot.say(avatar)
                except DiscordUser.DoesNotExist:
                    await self.bot.say("```Can't find discord user```")
                    update_display_names(self.bot.servers)

    @commands.command(pass_context=True)
    @mod_command
    async def game(self, ctx, *args):
        """Change bot's status"""
        game = ' '.join(args)
        if not game:
            await self.bot.say('`How to use: "!game Name"`')
        else:
            DiscordSettings.objects.filter(key='game').update(value=game)
            await self.bot.change_presence(game=discord.Game(name=game))
            await self.bot.say('Status changed', delete_after=15)

    @commands.command(hidden=True)
    async def shles(self):
        """SHLES"""
        await self.bot.say(DiscordLink.objects.get(key='shles'))

    @commands.command()
    async def ip(self):
        """Напомните ип плс"""
        await self.bot.say(str(DiscordSettings.objects.get(key='ip')) + ' <:OSsloth:230773934197440522>')

    @commands.command(pass_context=True, hidden=True)
    async def low(self, ctx):
        if ctx.message.author.id == '127135903125733376':
            await self.bot.say(DiscordLink.objects.get(key='low'))
        else:
            await self.bot.say('<:bearrion:230370930600312832>')

    @commands.command()
    async def cytube(self):
        """Для тех кто не умеет добавлять сайты в закладки"""
        cytube_url = DiscordLink.objects.get(key='cytube')
        movies_url = DiscordLink.objects.get(key='movies')
        await self.bot.say('`Смотреть` <:bearrion:230370930600312832> {0}\n'
                           '`Брать кинцо` <:cruzhulk:230370931065749514> {1}'.format(cytube_url, movies_url))

    @commands.command()
    async def free(self):
        """Holy scriptures"""
        await self.bot.say('`Живи молодым и умри молодым` {}'.format(DiscordLink.objects.get(key='free')))

    @commands.command()
    async def choose(self, *choices: str):
        """Chooses between two items"""
        await self.bot.say(random.choice(choices))

    @commands.command(hidden=True)
    async def friday(self):
        await self.bot.say(DiscordLink.objects.get(key='friday'))

    @commands.command()
    async def roll(self):
        """Rolls from 1 to 100"""
        await self.bot.say(random.randint(1, 100))

    @commands.command(hidden=True)
    async def firstrule(self):
        await self.bot.say('Never hook first <:smart:282452131552690176>')

    @commands.command(hidden=True)
    async def secondrule(self):
        await self.bot.say("You can't counter Pharah <:Kappa:230228691945390080>")

    @commands.command(hidden=True)
    async def thirdrule(self):
        await self.bot.say("Ко мне говно <:4Head:230227653783846912>")

    @commands.group(pass_context=True)
    async def gachi(self, ctx):
        """Take it boy"""
        if not ctx.invoked_subcommand:
            gachi_obj = get_random_entry(Gachi)
            if gachi_obj is not None:
                await self.bot.say(gachi_obj.url)

    @gachi.command(pass_context=True)
    @mod_command
    async def add(self, ctx, url: str):
        # Add regex for links
        Gachi.objects.create(url=url)
        await self.bot.say('{} added'.format(url))


def setup(bot):
    bot.add_cog(General(bot))

import logging

import discord
from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument

from discordbot.cogs.utils.checks import mod_command
from discordbot.models import Counter, CounterGroup

logger = logging.getLogger('botLogger.counters')


class Counters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counter_aliases = dict.fromkeys(
            ['kill', 'death', 'trup'], 'bodycount_killed')
        self.counter_aliases.update(dict.fromkeys(['save'], 'bodycount_saved'))

    async def counter_info(self, ctx):
        try:
            group = CounterGroup.objects.get(name=ctx.command.name)
            await ctx.send(embed=group.to_embed())
        except CounterGroup.DoesNotExist:
            counter = Counter.objects.get(name=ctx.command.name)
            await ctx.send(embed=group.to_embed())

    async def increment_counter(self, ctx, name):
        counter = Counter.objects.get(name=name)
        counter.increment_value()
        if counter.group and counter.group.latest_counter_streak >= 3:
            await ctx.send(f'{counter} is on {counter.group.latest_counter_streak} streak!')
        await ctx.send(
            f'Counter {counter} incremented by 1. Current value {counter.value}')

    async def decrement_counter(self, ctx, name):
        counter = Counter.objects.get(name=name)
        counter.decrement_value()
        await ctx.send(
            f'Counter {counter} decremented by 1. Current value {counter.value}')

    @commands.group()
    async def bodycount(self, ctx):
        if not ctx.invoked_subcommand:
            await self.counter_info(ctx)

    @bodycount.command()
    @mod_command
    async def add(self, ctx, alias):
        if alias in self.counter_aliases.keys():
            counter_name = self.counter_aliases.get(alias)
            await self.increment_counter(ctx, counter_name)

    @bodycount.command()
    @mod_command
    async def remove(self, ctx, alias):
        if alias in self.counter_aliases.keys():
            counter_name = self.counter_aliases.get(alias)
            await self.decrement_counter(ctx, counter_name)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'alias':
                avalilable_aliases = ', '.join(self.counter_aliases.keys())
                await ctx.send(
                    content=f'Command {ctx.command} is missing required arguments: `{error.param.name}`\n'
                            f'Available aliases are: {avalilable_aliases}'
                )
        elif hasattr(error, 'original') and \
                isinstance(error.original, (Counter.DoesNotExist, CounterGroup.DoesNotExist)):
            await ctx.send(f'Something wrong with {ctx.command.name} counter!')


def setup(bot):
    bot.add_cog(Counters(bot))

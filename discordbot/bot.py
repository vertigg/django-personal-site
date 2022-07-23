import logging
import os
import sys

import discord
from discord.ext import commands

from apps import setup_django

setup_django()
logger = logging.getLogger('discordbot')

intents = discord.Intents.default()
intents.members = True


bot = commands.Bot(
    command_prefix='!',
    description='Super duper halal bot for clowans. List of commands below',
    intents=intents
)


@bot.event
async def on_ready():
    from discordbot.models import DiscordSettings
    game = discord.Game(DiscordSettings.get_setting('game', default='No game'))
    await bot.change_presence(activity=game)
    logger.info('Logged in as %s:%s', bot.user.name, bot.user.id)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)


def load_cogs():
    cogs = ['admin', 'general', 'markov', 'mix', 'wikipedia']
    logger.info("Loading cogs...")
    for cog in cogs:
        try:
            if "cogs." not in cog:
                cog = "cogs." + cog
                bot.load_extension(cog)
                logger.info("%s loaded", cog)
        except (AttributeError, ImportError) as ex:
            logger.error("%s", ex)


if __name__ == '__main__':
    from django.conf import settings
    logger.info('Script started')
    token = settings.DISCORD_TEST_TOKEN if os.getenv('DISCORD_TEST', None) \
        else settings.DISCORD_BOT_TOKEN
    load_cogs()
    logger.info(sys.version)
    bot.run(token, reconnect=True)

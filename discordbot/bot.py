import logging
import os
import sys

import discord
from discord.ext import commands

from apps import setup_django

setup_django()
logging.config.fileConfig('discordbot/logger.ini')
discord_logger = logging.getLogger('discordLogger')
logger = logging.getLogger('botLogger')


bot = commands.Bot(command_prefix='!',
                   description='Super duper halal bot for clowans. List of commands below')


@bot.event
async def on_ready():
    from discordbot.models import DiscordSettings
    game = discord.Game(DiscordSettings.objects.get(key='game').value)
    await bot.change_presence(activity=game)
    logger.info(f'Logged in as {bot.user.name}:{bot.user.id}')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)


def load_cogs():
    cogs = ['admin', 'general', 'overwatch', 'mix', 'django', 'counters',
            'brawl', 'warframe', 'killing_floor', 'wikipedia', 'markov']
    logger.info("Loading cogs...")
    for cog in cogs:
        try:
            if "cogs." not in cog:
                cog = "cogs." + cog
                bot.load_extension(cog)
                logger.info(f"{cog} loaded")
        except (AttributeError, ImportError) as ex:
            logger.error("%s", ex)


if __name__ == '__main__':
    from discordbot.credentials import BOT_TOKEN, TEST_TOKEN
    logger.info('Script started')
    token = TEST_TOKEN if os.getenv('DISCORD_TEST', None) else BOT_TOKEN
    load_cogs()
    logger.info(sys.version)
    bot.run(token, reconnect=True)

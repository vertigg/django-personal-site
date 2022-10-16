import asyncio
import logging
import os

import discord
from discord.ext.commands import Bot

from apps import setup_django

logger = logging.getLogger('discordbot')

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True


bot = Bot(
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


@bot.event
async def on_message_delete(message):
    logger.info(
        'Message deleted: Author %s, Content "%s", Attachments: %s',
        message.author.id, message.content, len(message.attachments)
    )
    if message.attachments:
        logger.info(', '.join([att.url for att in message.attachments]))


async def load_cogs():
    cogs = ['admin', 'general', 'markov', 'mix', 'wikipedia']
    logger.info("Loading extensions...")
    for cog in cogs:
        try:
            await bot.load_extension("cogs." + cog)
            logger.info("'%s' extension loaded", cog)
        except (AttributeError, ImportError) as ex:
            logger.error("%s", ex)


async def main():
    from django.conf import settings
    logger.info('Script started')
    setup_django()
    token = settings.DISCORD_TEST_TOKEN if os.getenv('DISCORD_TEST', None) \
        else settings.DISCORD_BOT_TOKEN
    async with bot:
        await load_cogs()
        await bot.start(token, reconnect=True)

asyncio.run(main())

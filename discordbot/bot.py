import logging
import os
import sys
import discord
from discord.ext import commands


def __setup_django(root_path):
    import django
    os.chdir(root_path)
    sys.path.append(root_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "VertigoProject.settings")
    django.setup()

if os.name == 'nt':
    PROJECT_PATH = "C:\\Users\\EpicWin\\Desktop\\HomeSite"
else:
    PROJECT_PATH = '/home/vertigo/homesite'
__setup_django(PROJECT_PATH)

logging.config.fileConfig('discordbot/logger.ini')
discord_logger = logging.getLogger('discordLogger')
logger = logging.getLogger('botLogger')

from discordbot.models import DiscordSettings
from discordbot.credentials import BOT_TOKEN, TEST_TOKEN

bot = commands.Bot(command_prefix='!',
                   description='Super duper halal bot for clowans. List of commands below')


@bot.event
async def on_ready():
    game = discord.Game(DiscordSettings.objects.get(key='game').value)
    await bot.change_presence(activity=game)
    logger.info('Logged in as {0}:{1}'.format(bot.user.name, bot.user.id))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)


def load_cogs():
    cogs = ['admin', 'general', 'overwatch', 'mix', 'django',
            'brawl', 'warframe', 'killing_floor', 'wikipedia']
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
    logger.info('Script started')
    load_cogs()
    logger.info(sys.version)
    bot.run(BOT_TOKEN, reconnect=True)

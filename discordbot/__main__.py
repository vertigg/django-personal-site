"""
Entrypoint for Discord bot
Run from root directory as "python -m discordbot"
"""
import os

import django

from discordbot.bot import TonyBot

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    bot = TonyBot()
    bot.run(bot.token, reconnect=True)

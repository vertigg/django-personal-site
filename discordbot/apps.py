import os
import sys

import django
from django.apps import AppConfig

BOT_PATH = os.getenv('BOT_PATH', '/home/vertigo/homesite') if os.name != 'nt' \
    else "C:\\Users\\EpicWin\\Desktop\\HomeSite"


def setup_django():
    os.chdir(BOT_PATH)
    sys.path.append(BOT_PATH)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "homesite.settings")
    django.setup()


class DiscordbotConfig(AppConfig):
    name = 'discordbot'

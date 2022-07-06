import os
import sys
from pathlib import Path

import django
from django.apps import AppConfig


def setup_django() -> None:
    """Helper function that allows using Django features in Discord bot"""
    app_path = Path(__file__).resolve().parent.parent
    os.chdir(app_path)
    sys.path.append(str(app_path))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()


class DiscordbotConfig(AppConfig):
    name = 'discordbot'

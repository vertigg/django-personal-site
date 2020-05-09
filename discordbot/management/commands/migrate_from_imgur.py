"""
One-shot script for migrating `mix` command images from external imgur album to
local media storage
"""

import hashlib
import os
from datetime import datetime

import pytz
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from imgurpython import ImgurClient
from tqdm import tqdm

from discordbot.models import MixImage
from main.management.commands.utils import AdvancedCommand


class Command(AdvancedCommand):
    logger_name = 'imgur_migrate'

    def handle(self, *args, **options):
        client = ImgurClient(settings.IMGUR_ID, settings.IMGUR_SECRET)
        data = client.get_album_images(settings.IMGUR_ALBUM)
        for image in tqdm(data):
            filename = os.path.basename(image.link)
            content = ContentFile(requests.get(image.link).content)
            md5 = hashlib.md5(content.read()).hexdigest()
            if MixImage.objects.filter(checksum=md5).exists():
                print(f'{filename} already exists')
                continue
            date = datetime.utcfromtimestamp(image.datetime).replace(tzinfo=pytz.UTC)
            obj = MixImage(date=date, author_id=150653379138289665)
            obj.image.save(filename, content, save=True)

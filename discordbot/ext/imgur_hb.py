import logging
from datetime import datetime

from imgurpython import ImgurClient
from .utils import botExceptionCatch
from discordbot.models import DiscordPicture
from discordbot.credentials import IMGUR

logger = logging.getLogger('botLogger')

def convert_time(unixtime):
    """Convert posix time to datetime for database record"""
    return datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')

@botExceptionCatch
def get_album():
    client = ImgurClient(IMGUR['id'], IMGUR['secret'])
    data = client.get_album_images(IMGUR['album'])
    if len(data) == 0: 
        return None
    pictures = {x.link : x.datetime for x in data}
    logger.info ('[IMGURHB] Database has been updated with {0} pictures'.format(len(pictures)))
    logger.info ('[IMGURHB] Client limits are {0}/12500'.format(client.credits['ClientRemaining']))
    return pictures


def limits():
    client = ImgurClient(IMGUR['id'], IMGUR['secret'])
    limits = client.credits
    return limits


@botExceptionCatch
def update():
    """Update imgur table"""

    pictures = get_album()

    if pictures is None or not isinstance(pictures, dict):
        return 'Imgur album is empty!'

    saved_piclist = DiscordPicture.objects.values_list('url', flat=True)
    for key, value in pictures.items():
        if not key in saved_piclist:
            DiscordPicture.objects.create(url = key, date = value)
    return 'Database has been updated with {} pictures'.format(len(pictures))
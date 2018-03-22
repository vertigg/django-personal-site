import logging
from datetime import datetime

from imgurpython import ImgurClient
from .utils import botExceptionCatch
from discordbot.models import DiscordPicture

logger = logging.getLogger('TonyBot')

def convert_time(unixtime):
    """Convert posix time to datetime for database record"""
    return datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')

@botExceptionCatch
def get_album(credentials):
    client = ImgurClient(credentials['id'], credentials['secret'])
    data = client.get_album_images(credentials['album'])
    if len(data) == 0: 
        return None
    pictures = {x.link : x.datetime for x in data}
    logger.info ('[IMGURHB] List updated with {0} pictures'.format(len(pictures)))
    logger.info ('[IMGURHB] Client limits are 12500/{0}'.format(client.credits['ClientRemaining']))
    return pictures


def limits(credentials):
    client = ImgurClient(credentials['id'], credentials['secret'])
    limits = client.credits
    return limits


@botExceptionCatch
def update(credentials):
    """Update imgur table"""

    pictures = get_album(credentials['imgur'])

    if pictures is None or not isinstance(pictures, dict):
        return 'Imgur album is empty!'

    saved_piclist = DiscordPicture.objects.values_list('url', flat=True)
    for key, value in pictures.items():
        if not key in saved_piclist:
            DiscordPicture.objects.create(url = key, date = value)
    return 'Database updated with {} pictures'.format(len(pictures))
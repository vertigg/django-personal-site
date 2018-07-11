import logging
from datetime import datetime

from imgurpython import ImgurClient
from .utils import botExceptionCatch
from discordbot.models import DiscordPicture
from discordbot.credentials import IMGUR
from time import time

logger = logging.getLogger('botLogger')

def convert_time(unixtime):
    """Convert posix time to datetime for database record"""
    return datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')

def compare_timestamps(timestamp):
    """Some great code down here"""
    difference = time() - timestamp
    if difference > 16070400:
        return 3
    elif difference > 7776000:
        return 2
    else:
        return 1

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

def get_random_picture():
    """Gets random picture from imgur table and sets new pid based on picture's age"""
    random_pic = DiscordPicture.objects.filter(pid__lt=2).order_by('?').first()
    if random_pic:
        id = random_pic.id
        current_pid = random_pic.pid
        new_pid = current_pid + compare_timestamps(random_pic.date)
        DiscordPicture.objects.filter(id=random_pic.id).update(pid=new_pid)
        return random_pic.url
    else:
        DiscordPicture.objects.all().update(pid=0)
        return get_random_picture()
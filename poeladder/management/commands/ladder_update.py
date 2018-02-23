import json
import logging
import os
import sys
import time

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import OperationalError
from django.utils import timezone

from discordbot.models import DiscordUser
from poeladder.models import PoeCharacter, PoeInfo, PoeLeague

start_time = time.time()

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    handlers = [
        logging.FileHandler('logs/ladder_update.log'),
        logging.StreamHandler()
    ])

POE_LEAGUES = 'http://api.pathofexile.com/leagues?type=main&compact=1'
POE_PROFILE = 'https://www.pathofexile.com/character-window/get-characters?accountName={}'
DB_TIMEOUT = 5

def update_ladders_table():
    try:
        leagues_data = json.loads(requests.get(POE_LEAGUES).text)
        PoeLeague.objects.get_or_create(name='Void')
        for league in leagues_data:
            l, created = PoeLeague.objects.get_or_create(name = league['id'])
            l.start_date = league['startAt']
            l.url = league['url']
            l.end_date = league['endAt']
            l.save(update_fields=['url', 'start_date', 'end_date'])

    except OperationalError as e:
        logging.info('{0}. Waiting {1} seconds'.format(e, DB_TIMEOUT))
        logging.error(repr(e))
        time.sleep(DB_TIMEOUT)
        update_ladders_table()
    
    except Exception as e:
        logging.error(repr(e))


def update_characters_table():
    query = DiscordUser.objects.exclude(poe_profile__exact='')
    poe_profiles = {x.id : x.poe_profile for x in query}

    try:
        for key, value in poe_profiles.items():
            r = requests.get(POE_PROFILE.format(value))
            characters = json.loads(r.text)

            if isinstance(characters, dict) and characters['error']:
                raise requests.RequestException(characters['error'])

            if characters:
                for character in characters:
                    p, created = PoeCharacter.objects.get_or_create(
                        name = character['name'],
                        league = PoeLeague.objects.get(name=character['league']),
                        profile = DiscordUser.objects.get(id=key))

                    p.class_name = character['class']
                    p.class_id = character['classId']
                    p.ascendancy_id = character['ascendancyClass']
                    p.level = character['level']
                    p.save(update_fields=['league', 'class_name', 'level', 'class_id', 'ascendancy_id'])

    except OperationalError as e:
        logging.info('{0}. Waiting {1} seconds'.format(e, DB_TIMEOUT))
        logging.error(repr(e))
        time.sleep(DB_TIMEOUT)
        update_characters_table()
    
    except Exception as e:
        logging.error(repr(e))

def update_ladder_info():
    info, created = PoeInfo.objects.get_or_create(key='last_update')
    info.timestamp = timezone.localtime()
    info.save(update_fields=['timestamp'])

class Command(BaseCommand):
    help = 'Updates PoE ladder'

    def handle(self, *args, **options):
        from django.conf import settings
        logging.info(start_time)
        update_ladders_table()
        update_characters_table()
        logging.info('Done in {} seconds'.format(round(time.time() - start_time, 2)))
        update_ladder_info()

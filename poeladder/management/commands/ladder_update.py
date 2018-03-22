import json
import logging
import time
from datetime import datetime

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import OperationalError
from django.utils import timezone
from django.conf import settings

from discordbot.models import DiscordUser
from poeladder.models import PoeCharacter, PoeInfo, PoeLeague

from .utils import retry_on_lock

    
start_time = time.time()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    handlers = [
        logging.FileHandler('logs/ladder_update.log'),
        logging.StreamHandler()
    ])

if settings.DEBUG:
    from django.db import connection

POE_LEAGUES = 'http://api.pathofexile.com/leagues?type=main&compact=1'
POE_PROFILE = 'https://pathofexile.com/character-window/get-characters?accountName={}'
DB_TIMEOUT = 10
DB_RETRIES = 5


@retry_on_lock(DB_TIMEOUT, retries=DB_RETRIES)
def update_ladders_table():
    leagues_api_data = json.loads(requests.get(POE_LEAGUES).text)
    query_list = list(PoeLeague.objects.values_list('name', flat=True))

    if not 'Void' in query_list:
        logging.info('New league: Void')
        PoeLeague.objects.create(name='Void')

    for league in leagues_api_data:
        if league['id'] not in query_list:
            # create new league
            logging.info('New league: {}'.format(league['id']))
            PoeLeague.objects.create(
                name = league['id'],
                url = league['url'],
                start_date = league['startAt'],
                end_date = league['endAt']
            )


@retry_on_lock(DB_TIMEOUT, retries=DB_RETRIES)
def update_characters_table():

    poe_profiles = {x[0] : x[1] for x in DiscordUser.objects.exclude(poe_profile__exact='').values_list('id', 'poe_profile')}
    poe_leagues = {x[0]:x[1] for x in PoeLeague.objects.values_list('name', 'id')}
    
    for key, value in poe_profiles.items():
        r = requests.get(POE_PROFILE.format(value))
        api_data = json.loads(r.text)

        if isinstance(api_data, dict) and api_data['error']:
            raise requests.RequestException(api_data['error'])

        if api_data:
            # get all api_data and convert to dict
            characters_queryset = PoeCharacter.objects.values_list('name', 'league__name', 'level', 'ascendancy_id')
            saved_characters = {x[0] : {'league':x[1], 'level':x[2], 'ascendancy_id':x[3]} for x in characters_queryset}

            for character in api_data:
                # check if character exists
                if character['name'] in saved_characters:
                    # update current
                    ch = saved_characters[character['name']]
                    if ch['league'] != character['league'] or ch['level'] != character['level'] or ch['ascendancy_id'] != character['ascendancyClass']:
                        logging.info('Updating {}'.format(character['name']))
                        p = PoeCharacter.objects.get(name=character['name'])
                        p.league_id = poe_leagues[character['league']]
                        p.class_name = character['class']
                        p.class_id = character['classId']
                        p.ascendancy_id = character['ascendancyClass']
                        p.level = character['level']
                        p.save(update_fields=['league_id', 'class_name', 'level', 'ascendancy_id', 'class_id'])

                else:
                    # create new
                    logging.info('New character: {}'.format(character['name']))
                    PoeCharacter.objects.create(
                        name = character['name'],
                        league_id = poe_leagues[character['league']],
                        profile_id = key,
                        class_name = character['class'],
                        class_id = character['classId'],
                        ascendancy_id = character['ascendancyClass'],
                        level = character['level'],
                    )


@retry_on_lock(DB_TIMEOUT, retries=DB_RETRIES)
def update_ladder_info():
    info, created = PoeInfo.objects.get_or_create(key='last_update')
    info.timestamp = timezone.localtime()
    info.save(update_fields=['timestamp'])


class Command(BaseCommand):
    help = 'Updates PoE ladder'

    def handle(self, *args, **options):
        logging.info(datetime.now())
        update_ladders_table()
        update_characters_table()
        update_ladder_info()
        logging.info('Done in {} seconds'.format(round(time.time() - start_time, 2)))
        if settings.DEBUG:
            logging.info('Total db queries: {}'.format(len(connection.queries)))

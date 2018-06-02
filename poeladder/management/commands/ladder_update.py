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

from .utils import retry_on_lock, detect_skills

start_time = time.time()

logging.basicConfig(
    level=logging.DEBUG,
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
POE_INFO = 'https://www.pathofexile.com/character-window/get-items?character={0}&accountName={1}'
DB_TIMEOUT = 10
DB_RETRIES = 5
session = requests.session()
cookies = {'POESESSID' : settings.POESESSID}


def get_main_skills(character, account):
    r = session.get(POE_INFO.format(character, account), cookies=cookies)
    if r.headers.get('X-Rate-Limit-Ip-State'):
        logging.debug(r.headers['X-Rate-Limit-Ip-State'])
    if r.status_code == 429:
        logging.error('Rate limited!')
        time.sleep(65)
        r = session.get(POE_INFO.format(character, account), cookies=cookies)
    data = json.loads(r.text)
    return detect_skills(data)


@retry_on_lock(DB_TIMEOUT, retries=DB_RETRIES)
def update_ladders_table():
    leagues_api_data = json.loads(session.get(POE_LEAGUES).text)
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
        r = session.get(POE_PROFILE.format(value))
        if r.status_code == 429:
            logging.error('Rate limited!')
            time.sleep(65)
            r = session.get(POE_PROFILE.format(value))
        elif r.status_code == 403:
            logging.error("Forbidden: 403. Can't access {} profile".format(value))
            continue
        api_data = json.loads(r.text)
        time.sleep(1.1)

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
                        p.experience = character['experience']

                        # If gems changed - update with new set
                        gems_qs = get_main_skills(character['name'], value)
                        if not set(p.gems.all().values_list('id', flat=True)) == set(gems_qs):
                            p.gems.clear()
                            p.gems.add(*gems_qs)

                        p.save(update_fields=['league_id', 'class_name', 'level', 'ascendancy_id', 'class_id', 'experience'])

                else:
                    # create new
                    logging.info('New character: {}'.format(character['name']))
                    p = PoeCharacter.objects.create(
                        name = character['name'],
                        league_id = poe_leagues[character['league']],
                        profile_id = key,
                        class_name = character['class'],
                        class_id = character['classId'],
                        ascendancy_id = character['ascendancyClass'],
                        level = character['level'],
                        experience = character['experience'],
                    )
                    gems_qs = get_main_skills(character['name'], value)
                    p.gems.add(*gems_qs)


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

import json
import logging
import time
from datetime import datetime

import requests
from django.conf import settings
from django.utils import timezone

from discordbot.models import DiscordUser
from main.management.commands.utils import AdvancedCommand
from poeladder.models import PoeCharacter, PoeInfo, PoeLeague

from .utils import detect_skills, requests_retry_session


class LadderUpdateController:

    POE_LEAGUES = 'http://api.pathofexile.com/leagues?type=main&compact=1'
    POE_PROFILE = 'https://pathofexile.com/character-window/get-characters?accountName={}'
    POE_INFO = 'https://www.pathofexile.com/character-window/get-items?character={0}&accountName={1}'

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.session = requests_retry_session()
        self.cookies = {'POESESSID': settings.POESESSID}
        self.leagues, self.league_names = self._get_local_leagues_info()
        self.profiles = {x[0]: x[1] for x in DiscordUser.objects
                         .exclude(poe_profile__exact='')
                         .values_list('id', 'poe_profile')}

    def _get_local_leagues_info(self):
        leagues = {x[0]: {'league_id': x[1], 'end_date': x[2]}
                   for x in PoeLeague.objects.values_list('name', 'id', 'end_date')}
        league_names = set(leagues.keys())
        return leagues, league_names

    def get_main_skills(self, character, account):
        r = self.session.get(self.POE_INFO.format(
            character, account), cookies=self.cookies)
        if r.headers.get('X-Rate-Limit-Ip-State'):
            self.logger.debug(r.headers['X-Rate-Limit-Ip-State'])
        if r.status_code == 429:
            self.logger.error('Rate limited!')
            time.sleep(65)
            r = self.session.get(self.POE_INFO.format(
                character, account), cookies=self.cookies)
        data = json.loads(r.text)
        return detect_skills(data)

    def _parse_league_datetime(self, str_datetime: str) -> datetime:
        if isinstance(str_datetime, str):
            return datetime.strptime(str_datetime, '%Y-%m-%dT%H:%M:%S%z')
        return None

    def update_leagues(self):
        league_api_data = json.loads(self.session.get(self.POE_LEAGUES).text)
        api_league_names = {x['id'] for x in league_api_data}

        # Remove old leagues
        difference = self.league_names.difference(api_league_names)
        if 'Void' in difference:
            difference.remove('Void')

        if difference:
            self.logger.info(f'Deleting {difference}')
            PoeLeague.objects.filter(name__in=difference).delete()

        for league in league_api_data:
            league_name = league.get('id')
            if league_name not in self.league_names:
                # Create new league
                self.logger.info(f'New league: {league["id"]}')
                PoeLeague.objects.create(
                    name=league['id'],
                    url=league['url'],
                    start_date=league['startAt'],
                    end_date=league['endAt']
                )
            # Check if league's end date changed
            elif self._parse_league_datetime(league['endAt']) != self.leagues[league_name]['end_date']:
                PoeLeague.objects.filter(name=league_name).update(end_date=league['endAt'])
                self.logger.info(
                    f'{league_name.capitalize()} league has '
                    f'been updated with new end date {league["endAt"]}')

        if 'Void' not in self.league_names:
            self.logger.info('New league: Void')
            PoeLeague.objects.create(name='Void')

        # Update local league info
        self.leagues, self.league_names = self._get_local_leagues_info()

    def _build_character_data(self, api_data):
        data = {}
        for entry in api_data:
            data[entry['name']] = entry
        return data

    def _delete_characters(self, characters: set):
        self.logger.info(f'Deleting characters {characters}')
        PoeCharacter.objects.filter(name__in=characters).delete()

    def _create_characters(self, data: dict, characters: set, discord_id: int, account: str):
        for name in characters:
            character = data.get(name)
            self.logger.info(f'New character: {name}')
            p = PoeCharacter.objects.create(
                name=name,
                league_id=self.leagues[character['league']]['league_id'],
                profile_id=discord_id,
                class_name=character['class'],
                class_id=character['classId'],
                ascendancy_id=character['ascendancyClass'],
                level=character['level'],
                experience=character['experience'],
            )
            gems_qs = self.get_main_skills(name, account)
            p.gems.add(*gems_qs)

    def _update_characters(self, data: dict, characters: set, account: str):
        chars_qs = PoeCharacter.objects.filter(profile__poe_profile=account).values_list(
            'name', 'league__name', 'level', 'ascendancy_id', 'experience')
        saved_characters = {x[0]: {'league': x[1],
                                   'level': x[2],
                                   'ascendancy_id': x[3],
                                   'experience': x[4]} for x in chars_qs}
        for name in characters:
            character = data.get(name)
            ch = saved_characters[character['name']]
            if ch['league'] != character['league'] \
                    or ch['experience'] != character['experience'] \
                    or ch['ascendancy_id'] != character['ascendancyClass']:
                self.logger.info(f'Updating {name}')
                p = PoeCharacter.objects.get(name=name)
                p.league_id = self.leagues[character['league']]['league_id']
                p.class_name = character['class']
                p.class_id = character['classId']
                p.ascendancy_id = character['ascendancyClass']
                p.level = character['level']
                p.experience = character['experience']

                # If gems changed - update with new set
                gems_qs = self.get_main_skills(name, account)
                if not set(p.gems.all().values_list('id', flat=True)) == set(gems_qs):
                    p.gems.clear()
                    p.gems.add(*gems_qs)

                p.save(update_fields=[
                    'league_id', 'class_name', 'level',
                    'ascendancy_id', 'class_id', 'experience'])

    def _unsub_user(self, account):
        profile = DiscordUser.objects.get(poe_profile=account)
        PoeCharacter.objects.filter(profile=profile).delete()
        profile.poe_profile = ''
        profile.save(update_fields=['poe_profile'])
        self.logger.info(f'{account} removed from ladder')

    def _get_account_data(self, account):
        """Retrieves PoE Account data with all characters"""
        r = self.session.get(self.POE_PROFILE.format(account))
        if r.status_code == 429:
            self.logger.error('Rate limited!')
            time.sleep(65)
            r = self.session.get(self.POE_PROFILE.format(account))
        elif r.status_code == 403:
            self.logger.error(f"Forbidden: 403. Can't access {account} profile")
            self._unsub_user(account)
            return
        elif r.status_code != 200:
            self.logger.error(f'Error requesting {account} {r.status_code}: {r.text}')
            return
        api_data = json.loads(r.text)
        time.sleep(1.1)

        if isinstance(api_data, dict) and api_data.get('error', None):
            raise requests.RequestException(
                f"Error requesting {account} {r.status_code}: {api_data['error']}")
        return api_data

    def update_characters(self):
        for discord_id, poe_account in self.profiles.items():
            api_data = self._get_account_data(poe_account)
            if api_data:
                data = self._build_character_data(api_data)
                api_characters = set([x.get('name') for x in api_data])
                local_characters = set([x.name for x in
                                        PoeCharacter.objects.filter(profile__poe_profile=poe_account)])

                new_characters = api_characters.difference(local_characters)
                deleted_characters = local_characters.difference(
                    api_characters)
                update_characters = api_characters.intersection(
                    local_characters)

                if deleted_characters:
                    self._delete_characters(deleted_characters)

                # Create new characters
                if new_characters:
                    self._create_characters(
                        data, new_characters, discord_id, poe_account)

                # Update existing
                if update_characters:
                    self._update_characters(
                        data, update_characters, poe_account)

    def update_ladder_info(self):
        info, _ = PoeInfo.objects.get_or_create(key='last_update')
        info.timestamp = timezone.localtime()
        info.save(update_fields=['timestamp'])

    def run(self):
        self.logger.info(datetime.now())
        self.update_leagues()
        self.update_characters()
        self.update_ladder_info()

        if settings.DEBUG:
            from django.db import connection
            self.logger.info(f'Total db queries: {len(connection.queries)}')


class Command(AdvancedCommand):
    help = 'Updates PoE ladder'
    logger_name = 'ladder_update'

    def handle(self, *args, **options):
        LadderUpdateController(self.logger).run()
        self.log_execution_time()

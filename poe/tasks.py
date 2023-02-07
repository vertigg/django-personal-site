import json
import logging
import time
from datetime import datetime
from typing import Any

import requests
from django.conf import settings
from django.utils import timezone
from rest_framework import status

from config.celery import UniqueNamedTask, app, register_task
from discordbot.models import DiscordUser
from poe.models import Character, League, PoeInfo
from poe.utils.session import requests_retry_session
from poe.utils.skills import detect_skills

logger = logging.getLogger(__name__)


@register_task
class LadderUpdateTask(UniqueNamedTask):
    POE_LEAGUES = 'http://api.pathofexile.com/leagues?type=main&compact=1'
    POE_PROFILE = 'https://pathofexile.com/character-window/get-characters?accountName={}'
    POE_INFO = 'https://pathofexile.com/character-window/get-items?character={0}&accountName={1}'

    def __init__(self):
        self.session = requests_retry_session()

    def _get_local_data(self) -> None:
        self.leagues, self.league_names = self._get_local_leagues_info()
        self.profiles = {x[0]: x[1] for x in DiscordUser.objects
                         .exclude(poe_profile__isnull=True)
                         .values_list('id', 'poe_profile')}

    def _get_character_league_id(self, character_data):
        # FIXME: Ugly ass hotfix for new temp leagues (thanks GGG)
        league = self.leagues.get(character_data['league'])
        return league.get('league_id') if league else League.objects.get(name='Void').id

    def _get_local_leagues_info(self):
        leagues = {x[0]: {'league_id': x[1], 'end_date': x[2]}
                   for x in League.objects.values_list('name', 'id', 'end_date')}
        league_names = set(leagues.keys())
        return leagues, league_names

    def get_main_skills(self, character: str, account: str):
        response = self.session.get(self.POE_INFO.format(character, account))
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            logger.debug(response.headers['X-Rate-Limit-Ip-State'])
            logger.error('Rate limited!')
            time.sleep(65)
            response = self.session.get(self.POE_INFO.format(character, account))
        if response.ok:
            data = json.loads(response.text)
            return detect_skills(data)
        return list()

    def _parse_league_datetime(self, str_datetime: str) -> datetime:
        if isinstance(str_datetime, str):
            return datetime.strptime(str_datetime, '%Y-%m-%dT%H:%M:%S%z')
        return None

    def update_leagues(self):
        league_api_data = self.session.get(self.POE_LEAGUES).json()
        api_league_names = {x['id'] for x in league_api_data}

        # Remove old leagues
        difference = self.league_names.difference(api_league_names)
        if 'Void' in difference:
            difference.remove('Void')

        if difference:
            logger.info('Deleting %s', difference)
            League.objects.filter(name__in=difference).delete()

        for league in league_api_data:
            league_name = league.get('id')
            if league_name not in self.league_names:
                # Create new league
                logger.info('New league: %s', league_name)
                League.objects.create(
                    name=league_name,
                    url=league['url'],
                    start_date=league['startAt'],
                    end_date=league['endAt']
                )
            # Check if league's end date changed
            elif self._parse_league_datetime(league['endAt']) != self.leagues[league_name]['end_date']:
                League.objects.filter(name=league_name).update(end_date=league['endAt'])
                logger.info(
                    '%s league has been updated with new end date %s',
                    league_name.capitalize(), league.get("endAt")
                )

        if 'Void' not in self.league_names:
            logger.info('New league: Void')
            League.objects.create(name='Void')

        # Update local league info
        self.leagues, self.league_names = self._get_local_leagues_info()

    def _delete_characters(self, characters: set):
        logger.info('Deleting characters %s', characters)
        Character.objects.filter(name__in=characters).delete()

    def _create_characters(self, data: dict, characters: set, discord_id: int, account: str):
        for name in characters:
            character = data.get(name)
            logger.info('New character: %s', name)
            league_id = self._get_character_league_id(character)
            p = Character.objects.create(
                name=name,
                league_id=league_id,
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
        chars_qs = Character.objects.filter(profile__poe_profile=account).values_list(
            'name', 'league__name', 'level', 'ascendancy_id', 'experience')
        saved_characters = {x[0]: {'league': x[1],
                                   'level': x[2],
                                   'ascendancy_id': x[3],
                                   'experience': x[4]} for x in chars_qs}
        for name in characters:
            character = data.get(name)
            ch = saved_characters[character['name']]
            league_id = self._get_character_league_id(character)
            if ch['league'] != character['league'] \
                    or ch['experience'] != character['experience'] \
                    or ch['ascendancy_id'] != character['ascendancyClass']:
                logger.info('Updating %s', name)
                p = Character.objects.get(name=name)
                p.league_id = league_id
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
                    'ascendancy_id', 'class_id', 'experience', 'modified'
                ])

    def _unsub_user(self, account: str):
        profile = DiscordUser.objects.get(poe_profile=account)
        Character.objects.filter(profile=profile).delete()
        profile.poe_profile = ''
        profile.save(update_fields=['poe_profile'])
        logger.info('%s removed from ladder', account)

    def _get_account_data(self, account: str) -> dict[str, Any]:
        """Retrieves PoE Account data with all characters"""
        response = self.session.get(self.POE_PROFILE.format(account))
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            logger.error('Rate limited!')
            time.sleep(65)
            response = self.session.get(self.POE_PROFILE.format(account))
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            logger.error("Forbidden: 403. Can't access %s profile", account)
            self._unsub_user(account)
            return
        elif not response.ok:
            logger.error('Error requesting %s %s: %s', account, response.status_code, response.text)
            return
        api_data = response.json()
        time.sleep(1.1)

        if isinstance(api_data, dict) and api_data.get('error', None):
            raise requests.RequestException(
                f"Error requesting {account} {response.status_code}: {api_data['error']}")
        return api_data

    def update_characters(self):
        for discord_id, poe_account in self.profiles.items():
            api_data = self._get_account_data(poe_account)
            if api_data:
                data = {entry['name']: entry for entry in api_data}
                api_characters = {x.get('name') for x in api_data}
                local_characters = {
                    x.name for x in
                    Character.objects.filter(profile__poe_profile=poe_account)
                }
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
        logger.info('Starting PoE ladder update')
        self._get_local_data()
        self.update_leagues()
        self.update_characters()
        self.update_ladder_info()

        if settings.DEBUG:
            from django.db import connection
            logger.info('Total db queries: %s', len(connection.queries))


@app.task()
def remove_related_characters(discord_id: int):
    """Removes all characters assosicated with DiscordUser"""
    Character.objects.filter(profile=discord_id).delete()

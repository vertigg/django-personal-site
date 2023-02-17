import json
import logging
import time
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from rest_framework import status

from config.celery import UniqueNamedTask, app, register_task
from discordbot.models import DiscordUser
from poe.models import Character, League, PoeInfo
from poe.schema import CharacterSchema
from poe.utils.session import requests_retry_session
from poe.utils.skills import detect_skills

logger = logging.getLogger(__name__)


@register_task
class LadderUpdateTask(UniqueNamedTask):
    POE_LEAGUES = 'http://api.pathofexile.com/leagues?type=main&compact=1'
    POE_PROFILE = 'https://pathofexile.com/character-window/get-characters?accountName={}'
    POE_INFO = 'https://pathofexile.com/character-window/get-items?character={0}&accountName={1}'
    leagues = {}
    league_names = set()

    def __init__(self):
        self.session = requests_retry_session()

    def _get_local_data(self) -> None:
        self.leagues = self._get_local_leagues_info()
        self.league_names = set(self.leagues.keys())

    @property
    def profiles(self) -> dict[str, DiscordUser]:
        return dict(
            DiscordUser.objects.exclude(poe_profile__isnull=True)
            .values_list('id', 'poe_profile')
        )

    def _get_character_league_id(self, league_name: str):
        # FIXME: Ugly ass hotfix for new temp leagues (thanks GGG)
        league = self.leagues.get(league_name)
        return league.get('league_id') if league else League.objects.get(name='Void').id

    def _get_local_leagues_info(self):
        return {x[0]: {'league_id': x[1], 'end_date': x[2]}
                for x in League.objects.values_list('name', 'id', 'end_date')}

    def get_main_skills(self, character: str, account: str):
        response = self.session.get(self.POE_INFO.format(character, account))
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            logger.debug(response.headers['X-Rate-Limit-Ip-State'])
            logger.error('Rate limited!')
            time.sleep(61)
            response = self.session.get(self.POE_INFO.format(character, account))
        if response.ok:
            data = json.loads(response.text)
            return detect_skills(data)
        return []

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

    def _delete_characters(self, characters: set[str]):
        logger.info('Deleting characters %s', characters)
        Character.objects.filter(name__in=characters).delete()

    def _create_characters(self, data: list[CharacterSchema], discord_id: int, account: str):
        for character in data:
            logger.info('New character: %s', character.name)
            league_id = self._get_character_league_id(character.league)
            new_character = Character.objects.create(
                name=character.name,
                league_id=league_id,
                profile_id=discord_id,
                class_name=character.class_name,
                class_id=character.class_id,
                ascendancy_id=character.ascendancy_id,
                level=character.level,
                experience=character.experience,
                expired=character.expired
            )
            gems_qs = self.get_main_skills(character.name, account)
            new_character.gems.add(*gems_qs)

    def _update_characters(self, data: list[CharacterSchema], account_name: str):
        saved_characters = {
            x.name: x for x in Character.objects.filter(
                profile__poe_profile=account_name).select_related('league')
        }
        for character in data:
            existing_character = saved_characters[character.name]
            league_id = self._get_character_league_id(character.league)
            if any([
                existing_character.league.name != character.league,
                existing_character.experience != character.experience,
                existing_character.ascendancy_id != character.ascendancy_id,
                existing_character.expired != character.expired,
            ]):
                logger.info('Updating %s', character.name)
                existing_character.update(
                    league_id=league_id,
                    class_name=character.class_name,
                    class_id=character.class_id,
                    ascendancy_id=character.ascendancy_id,
                    level=character.level,
                    experience=character.experience,
                    expired=character.expired,
                )
                # If gems changed - update with new set
                gems_qs = self.get_main_skills(character.name, account_name)
                if not set(existing_character.gems.values_list('id', flat=True)) == set(gems_qs):
                    existing_character.gems.clear()
                    existing_character.gems.add(*gems_qs)

    def _unsub_user(self, account: str):
        profile = DiscordUser.objects.get(poe_profile=account)
        Character.objects.filter(profile=profile).delete()
        profile.poe_profile = None
        profile.save(update_fields=['poe_profile'])
        logger.info('%s removed from ladder', account)

    def _get_account_data(self, account_name: str) -> list[CharacterSchema]:
        """Retrieves PoE Account data with all characters"""
        response = self.session.get(self.POE_PROFILE.format(account_name))
        match response.status_code:
            case status.HTTP_200_OK:
                # TODO: Handle HTML responses during maintenance
                ...
            case status.HTTP_429_TOO_MANY_REQUESTS:
                logger.error('Rate limited!')
                time.sleep(65)
                return self._get_account_data(account_name)
            case status.HTTP_403_FORBIDDEN:
                logger.error("Forbidden: 403. Can't access %s profile", account_name)
                self._unsub_user(account_name)
                return
            case _:
                logger.error(
                    'Error requesting %s %s: %s',
                    account_name, response.status_code, response.text
                )
                return
        api_data = response.json()
        time.sleep(1)
        if isinstance(api_data, dict) and 'error' in api_data:
            logger.error(
                "Error requesting %s %d: %s",
                account_name, response.status_code, api_data['error']
            )
            return
        return [CharacterSchema(**x) for x in api_data]

    def main(self):
        for discord_id, poe_account in self.profiles.items():
            if api_data := self._get_account_data(poe_account):
                api_characters = {x.name for x in api_data}
                local_characters = set(
                    Character.objects.filter(profile__poe_profile=poe_account)
                    .values_list('name', flat=True)
                )

                if deleted_characters := local_characters.difference(api_characters):
                    self._delete_characters(deleted_characters)

                # Create new characters
                if new_characters := api_characters.difference(local_characters):
                    new_data = [x for x in api_data if x.name in new_characters]
                    self._create_characters(new_data, discord_id, poe_account)

                # Update existing
                if chars_to_update := api_characters.intersection(local_characters):
                    update_data = [x for x in api_data if x.name in chars_to_update]
                    self._update_characters(update_data, poe_account)

    def update_ladder_info(self):
        PoeInfo.objects.update_or_create(key='last_update', defaults={
            'timestamp': timezone.localtime()
        })

    def run(self):
        logger.info('Starting PoE ladder update')
        self._get_local_data()
        self.update_leagues()
        self.main()
        self.update_ladder_info()

        if settings.DEBUG:
            from django.db import connection
            logger.info('Total db queries: %s', len(connection.queries))


@app.task()
def remove_related_characters(discord_id: int):
    """Removes all characters assosicated with DiscordUser"""
    Character.objects.filter(profile=discord_id).delete()

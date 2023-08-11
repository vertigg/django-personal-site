import logging

from celery import Task, chain
from django.conf import settings
from django.utils import timezone
from rest_framework import status

from config.celery import UniqueNamedTask, app, register_task
from discordbot.models import DiscordUser
from poe.config import settings as poe_settings
from poe.models import Character, League, PoeInfo
from poe.schema import CharacterSchema
from poe.utils.api import Client, PoEClientException
from poe.utils.pob import PoBWrapper
from poe.utils.skills import detect_active_skills

logger = logging.getLogger(__name__)


@register_task
class LadderUpdateTask(UniqueNamedTask):
    leagues = {}
    league_names = set()
    character_tasks: list[Task] = []

    def __init__(self):
        self.client = Client()

    def refresh_local_league_data(self) -> None:
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

    def update_leagues(self):
        data = self.client.get_league_data()
        api_league_names = {league.name for league in data}

        # Remove old leagues
        difference = self.league_names.difference(api_league_names)
        if 'Void' in difference:
            difference.remove('Void')

        if difference:
            logger.info('Deleting %s', difference)
            League.objects.filter(name__in=difference).delete()

        for league in data:
            if league.name not in self.league_names:
                # Create new league
                logger.info('New league: %s', league.name)
                League.objects.create(
                    name=league.name,
                    url=league.url,
                    start_date=league.start_date,
                    end_date=league.end_date
                )
            # Check if league's end date changed
            elif league.end_date != self.leagues[league.name]['end_date']:
                League.objects.filter(name=league.name).update(end_date=league.end_date)
                logger.info(
                    '%s league has been updated with new end date %s',
                    league.name.capitalize(), league.end_date
                )

        if 'Void' not in self.league_names:
            logger.info('New league: Void')
            League.objects.create(name='Void')

        # Update local league info
        self.refresh_local_league_data()

    def _delete_characters(self, characters: set[str]):
        logger.info('Deleting characters %s', characters)
        Character.objects.filter(name__in=characters).delete()

    def _create_characters(self, data: list[CharacterSchema], discord_id: int, account_name: str):
        for character in data:
            logger.info('New character: %s', character.name)
            league_id = self._get_character_league_id(character.league)
            Character.objects.create(
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
            self.character_tasks.append(UpdateCharacterMetadataTask.si(
                account_name, character.name
            ))

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
                self.character_tasks.append(UpdateCharacterMetadataTask.si(
                    account_name, existing_character.name
                ))

    def _unsub_user(self, account_name: str):
        profile = DiscordUser.objects.get(poe_profile=account_name)
        Character.objects.filter(profile=profile).delete()
        profile.poe_profile = None
        profile.save(update_fields=['poe_profile'])
        logger.info('%s removed from ladder', account_name)

    def _get_account_data(self, account_name: str) -> list[CharacterSchema]:
        """Retrieves PoE Account data with all characters"""
        try:
            return self.client.get_character_list(account_name)
        except PoEClientException as exc:
            if exc.status_code == status.HTTP_403_FORBIDDEN:
                logger.error("Forbidden: 403. Can't access %s profile", account_name)
                self._unsub_user(account_name)
            logger.error(exc)

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
        self.character_tasks = []
        self.refresh_local_league_data()
        self.update_leagues()
        self.main()
        self.update_ladder_info()

        if self.character_tasks:
            tasks = chain(*self.character_tasks)
            tasks.apply_async()

        if settings.DEBUG:
            from django.db import connection
            logger.info('Total db queries: %s', len(connection.queries))


@register_task
class UpdateCharacterMetadataTask(Task):

    def __init__(self):
        self.client = Client()

    def detect_main_skills(self, character: Character, account: str):
        logger.info('Detecting main skills for character: %s', character.name)
        try:
            items_data = self.client.get_character_items(account, character.name)
        except PoEClientException:
            logger.error('Unable to get gem data for %s: %s', account, character.name)
            return
        gem_ids = detect_active_skills(items_data)
        character.gems.clear()
        character.gems.add(*gem_ids)
        return items_data

    def set_pob_data(self, character: Character, account: str, items_data: dict):
        try:
            tree_data = self.client.get_character_skill_tree(account, character.name)
            wrapper = PoBWrapper(character.name, items_data, tree_data)
            data = wrapper.get_character_pob_data(character.name)
            logger.info(data)
            character.life = data.life
            character.es = data.es
            character.combined_dps = data.combined_dps
            character.save(update_fields=['life', 'es', 'combined_dps'])
            logger.info('Updating character with PoB data: %s', character.name)
        except Exception as exc:
            logger.error(exc)

    def run(self, account_name: str, character_name: str):
        logger.info('Received task for %s - %s', account_name, character_name)
        character = Character.objects.filter(name=character_name).first()
        if not character:
            logger.error('Aborting task: %s character not found', character_name)
            return
        if character.expired or character.level < poe_settings.LADDER_METADATA_MIN_LEVEL:
            return
        items_data = self.detect_main_skills(character, account_name)
        if items_data:
            self.set_pob_data(character, account_name, items_data)
        logger.info('Character %s updated with additional data', character_name)


@app.task()
def remove_related_characters(discord_id: int):
    """Removes all characters assosicated with DiscordUser"""
    Character.objects.filter(profile=discord_id).delete()

from poe.exceptions import PoEClientException
from poe.schema import CharacterSchema, LeagueSchema
from poe.utils.session import requests_retry_session


class Client:
    LEAGUES_API = 'http://api.pathofexile.com/leagues?type=main&compact=1'
    PROFILE_API = 'https://pathofexile.com/character-window/get-characters?accountName={}'
    ITEMS_API = 'https://pathofexile.com/character-window/get-items?character={0}&accountName={1}'
    TREE_API = 'https://pathofexile.com/character-window/get-passive-skills?accountName={0}&character={1}'

    def __init__(self) -> None:
        self.session = requests_retry_session()

    def _get(self, url: str):
        response = self.session.request('GET', url)
        if not response.ok:
            raise PoEClientException(
                msg=f'Request returned with status {response.status_code}. {response.json()}',
                status_code=response.status_code
            )
        return response.json()

    def get_league_data(self) -> list[LeagueSchema]:
        return [LeagueSchema(**x) for x in self._get(self.LEAGUES_API)]

    def get_character_list(self, account_name: str) -> list[CharacterSchema]:
        return [CharacterSchema(**x) for x in self._get(self.PROFILE_API.format(account_name))]

    def get_character_items(self, account_name: str, character_name: str):
        return self._get(self.ITEMS_API.format(character_name, account_name))

    def get_character_skill_tree(self, account_name: str, character_name: str):
        return self._get(self.TREE_API.format(account_name, character_name))

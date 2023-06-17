from poe.utils.session import requests_retry_session
from poe.schema import LeagueSchema


class Client:
    LEAGUES_API = 'http://api.pathofexile.com/leagues?type=main&compact=1'
    PROFILE_API = 'https://pathofexile.com/character-window/get-characters?accountName={}'
    ITEMS_API = 'https://pathofexile.com/character-window/get-items?character={0}&accountName={1}'

    def __init__(self) -> None:
        self.session = requests_retry_session()

    def get_league_data(self) -> list[LeagueSchema]:
        return [LeagueSchema(**x) for x in self.session.get(self.LEAGUES_API).json()]

    def get_characters(self, account_name: str):
        return self.session.get(self.PROFILE_API.format(account_name))

    def get_items_data(self, account_name: str, character_name: str):
        return self.session.get(self.ITEMS_API.format(character_name, account_name))

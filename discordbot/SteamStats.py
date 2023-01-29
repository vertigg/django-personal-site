import logging
from dataclasses import dataclass
from os import getenv

import gspread
import pandas as pd
import requests
from dotenv import load_dotenv
from gspread import Worksheet
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()
logger = logging.getLogger()


STEAM_API_KEY = getenv('STEAM_API_KEY')
BASE_API = 'http://api.steampowered.com/ISteamUserStats/'
SCHEMA_API = BASE_API + 'GetSchemaForGame/v2/'
PLAYER_STATS_API = BASE_API + 'GetPlayerAchievements/v1/'


@dataclass
class Player:
    steam_id: int
    name: str


@dataclass
class Game:
    game_id: int
    name: str
    players: list[Player]


def main(worksheet: Worksheet, game: Game) -> None:
    schema_params = {'key': STEAM_API_KEY, 'appid': game.game_id, 'l': 'eng', 'format': 'json'}
    master_data = requests.get(SCHEMA_API, params=schema_params).json()
    dataframe = pd.DataFrame(master_data['game']['availableGameStats']['achievements'])
    dataframe = dataframe[['name', 'displayName', 'description', 'icon']]

    for player in game.players:
        payload = {'key': STEAM_API_KEY, 'appid': game.game_id, 'steamid': player.steam_id}
        data = requests.get(PLAYER_STATS_API, params=payload).json()
        df = pd.DataFrame(data['playerstats']['achievements'])
        df = df.set_index('apiname').rename(columns={'achieved': player.name})[[player.name]]
        dataframe = dataframe.join(df, on='name')

    dataframe['icon'] = dataframe['icon'].apply(lambda x: f"=IMAGE(\"{x}\", 2)")
    dataframe.rename(columns={
        'displayName': 'Achievement Name',
        'description': 'Description',
        'icon': 'Icon'
    }, inplace=True)

    columns = ['Achievement Name', 'Description', 'Icon'] + [x.name for x in game.players]
    dataframe = dataframe[columns]
    worksheet.update(
        'A6:I319',
        [dataframe.columns.values.tolist()] + dataframe.values.tolist(),
        value_input_option='USER_ENTERED'
    )


def get_worksheet(spreadsheet_name: str, worksheet_name: str) -> Worksheet:
    """Authorize into Google Drive and return worksheet by name"""
    logger.info('Logging into Google Drive...')
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    try:
        gcredentials = ServiceAccountCredentials.from_json_keyfile_name(
            'discordbot/google-drive.json', scope)
        gs = gspread.authorize(gcredentials)
        return gs.open(spreadsheet_name).worksheet(worksheet_name)
    except gspread.SpreadsheetNotFound as exc:
        logger.error("Can't open a file with given name")
        raise exc


if __name__ == '__main__':
    logger.info('Script started')
    player_1 = Player(steam_id=76561197999838208, name='Vertig')
    kf2 = Game(game_id=232090, name='Killing Floor 2', players=[player_1])
    worksheet = get_worksheet('Steam Achievements', 'KF2New')
    main(worksheet=worksheet, game=kf2)

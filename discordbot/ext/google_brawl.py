"""Module for brawl command"""

import logging
from random import choice

import gspread
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

from discordbot.models import Brawl, DiscordSettings

logger = logging.getLogger('TonyBot')

def authorize_google(json_file, token):
    try:
        gscope = ['https://spreadsheets.google.com/feeds',
                  'https://www.googleapis.com/auth/drive.metadata.readonly']
        gcredentials = ServiceAccountCredentials.from_json_keyfile_name(
            json_file, gscope)
        service = discovery.build('drive', 'v3', credentials=gcredentials)
        response = service.changes().list(pageToken=token).execute()
        logger.debug(response)
        logger.info('[GSPREAD] Current state: {0}, New state: {1}'.format(
            token, response['newStartPageToken']))
        return gcredentials, response
    except Exception as e:
        logger.error('[{0}] {1}'.format(__name__, e))
        return None, None


def read_spreadsheet(gcredentials, spreadsheet):
    try:
        gcs = gspread.authorize(gcredentials)
        brawl_sh = gcs.open(spreadsheet).sheet1
        # Get raw data from google sheet
        raw_data = [list(brawl_sh.col_values(i+1)) for i in range(brawl_sh.col_count)]
        # Filter lists for empty cells
        filtered_data = list(list(filter(None, column)) for column in raw_data)

        if 0 in list(map(len, filtered_data)):
            logger.error("[GSPREAD] Brawl lists can't be empty!")
            return None
        else:
            update_brawl_table(raw_data)
            return filtered_data
    except Exception as e:
        logger.error('[{0}] {1}'.format(__name__, e))
        return None


def check_for_updates():

    json_file = DiscordSettings.objects.get(key='json').value
    token = DiscordSettings.objects.get(key='token').value
    spreadsheet = DiscordSettings.objects.get(key='spreadsheet').value

    gcredentials, response = authorize_google(json_file, token)
    
    if response is not None and 'newStartPageToken' in response:

        # Use cached table if response token is the same as saved one
        if token == response.get('newStartPageToken'):
            logger.info('[GSPREAD] Brawl lists are the same.')
            return get_brawl_table()

        # Update token if token is different, but brawl spreadsheet is not in response
        elif token != response.get('newStartPageToken') and spreadsheet not in str(response):
            logger.info('[GSPREAD]: Brawl dictionary is not in response. New page token is {}'.format(
                response.get('newStartPageToken')))
            logger.info('[GSPREAD]: Brawl lists are the same.')
            DiscordSettings.objects.filter(key='token').update(value=response.get('newStartPageToken'))
            return get_brawl_table() 

        # Try to get new brawl_list and update db table
        else:
            brawl_list = read_spreadsheet(gcredentials, spreadsheet)
            if brawl_list is not None:
                DiscordSettings.objects.filter(key='token').update(value=response.get('newStartPageToken'))
                logger.info('[GSPREAD] Brawl lists updated.')
            else:
                logger.error("[GSPREAD] Using cached brawl table")
                brawl_list = get_brawl_table()
            return brawl_list
    else:
        logger.error("Can't connect to google drive. Please check logs for more info")
        brawl_list = get_brawl_table()
        return brawl_list


def randomize_phrase(brawl_list):
    message = '{r[0]} {r[1]} {r[3]} {r[4]} и {r[5]} {r[2]}'
    if brawl_list:
        phrase_list = [choice(x) for x in brawl_list]
        return message.format(r=phrase_list)
    else:
        return ('`Something wrong with brawl lists. Please check logs for more info`')


def get_brawl_table():
    try:
        raw_data = Brawl.objects.all().values_list()
        column_lists = list(map(list, zip(*raw_data)))
        column_lists.pop(0)
        filtered_lists = list(list(filter(None, column)) for column in column_lists)
        return filtered_lists
    except Exception as e:
        logger.error('[{0}] {1}'.format(__name__, e))
        return None


def update_brawl_table(brawl_list):
    Brawl.objects.all().delete()
    insert_list = []
    for i in range(len(brawl_list[0])):
        insert_list.append(Brawl(
            name = brawl_list[0][i],
            action = brawl_list[1][i],
            tool = brawl_list[2][i],
            action2 = brawl_list[3][i],
            place = brawl_list[4][i],
            victim = brawl_list[5][i]
        ))
    Brawl.objects.bulk_create(insert_list)

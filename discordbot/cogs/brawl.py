import logging
from random import choice

import gspread
from apiclient import discovery
from discord.ext import commands
from discordbot.models import Brawl, DiscordLink, DiscordSettings
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger('discordbot.brawl')


class GoogleBrawl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.brawl_list = self.check_for_updates()

    @commands.group()
    async def brawl(self, ctx):
        """Kill me pls"""
        if not ctx.invoked_subcommand:
            await ctx.send(self.randomize_phrase(self.brawl_list))

    @brawl.command()
    async def update(self, ctx):
        """Update db from google spreadsheet"""
        self.brawl_list = self.check_for_updates()
        if self.brawl_list:
            await ctx.send('`Brawl table has been successfully updated`')
        else:
            await ctx.send("`Something wrong with brawl lists. Please check logs for more info`")

    @brawl.command()
    async def info(self, ctx):
        """Brawl Spreadsheet url"""
        await ctx.send(DiscordLink.objects.get(key='brawl_sheet'))

    def check_for_updates(self):
        json_file = DiscordSettings.get_setting('json')
        token = DiscordSettings.get_setting('token')
        spreadsheet = DiscordSettings.get_setting('spreadsheet')
        gcredentials, response = self.authorize_google(json_file, token)
        if response is not None and 'newStartPageToken' in response:
            response_token = response.get('newStartPageToken')
            if token == response_token:
                logger.info('Brawl lists are the same.')
                return self.get_brawl_table()
            if token != response_token and spreadsheet not in str(response):
                logger.info(
                    'Brawl dictionary is not in response. New page token is %s',
                    response_token
                )
                DiscordSettings.objects.filter(key='token').update(value=response_token)
                return self.get_brawl_table()
            brawl_list = self.read_spreadsheet(gcredentials, spreadsheet)
            if brawl_list is not None:
                DiscordSettings.objects.filter(key='token').update(
                    value=response_token)
                logger.info('Brawl lists updated.')
            else:
                logger.error("Using cached brawl table")
                brawl_list = self.get_brawl_table()
            return brawl_list
        else:
            logger.error(
                "Can't connect to google drive. Please check logs for more info")
            return self.get_brawl_table()

    def authorize_google(self, json_file_path: str, token: str):
        try:
            gscope = ['https://spreadsheets.google.com/feeds',
                      'https://www.googleapis.com/auth/drive.metadata.readonly']
            gcredentials = ServiceAccountCredentials.from_json_keyfile_name(
                json_file_path, gscope)
            service = discovery.build('drive', 'v3', credentials=gcredentials)
            response = service.changes().list(pageToken=token).execute()
            logger.debug(response)
            logger.info('Current state: {0}, New state: {1}'.format(
                token, response['newStartPageToken']))
            return gcredentials, response
        except Exception as ex:
            logger.error('[{0}] {1}'.format(__name__, ex))
            return None, None

    def read_spreadsheet(self, gcredentials, spreadsheet):
        try:
            gcs = gspread.authorize(gcredentials)
            brawl_sh = gcs.open(spreadsheet).sheet1
            raw_data = [list(brawl_sh.col_values(i + 1))
                        for i in range(brawl_sh.col_count)]
            filtered_data = list(list(filter(None, column))
                                 for column in raw_data)

            if 0 in list(map(len, filtered_data)):
                logger.error("Brawl lists can't be empty!")
                return None
            self.update_brawl_table(raw_data)
            return filtered_data
        except Exception as ex:
            logger.error('[{0}] {1}'.format(__name__, ex))
            return None

    def get_brawl_table(self):
        try:
            raw_data = Brawl.objects.all().values_list()
            column_lists = list(map(list, zip(*raw_data)))
            column_lists.pop(0)
            filtered_lists = list(list(filter(None, column))
                                  for column in column_lists)
            return filtered_lists
        except Exception as ex:
            logger.error('[{0}] {1}'.format(__name__, ex))
            return None

    def update_brawl_table(self, brawl_list):
        Brawl.objects.all().delete()
        insert_list = []
        for i in range(len(brawl_list[0])):
            insert_list.append(Brawl(
                name=brawl_list[0][i],
                action=brawl_list[1][i],
                tool=brawl_list[2][i],
                action2=brawl_list[3][i],
                place=brawl_list[4][i],
                victim=brawl_list[5][i]
            ))
        Brawl.objects.bulk_create(insert_list)

    def randomize_phrase(self, brawl_list):
        message = '{r[0]} {r[1]} {r[3]} {r[4]} и {r[5]} {r[2]}'
        if brawl_list:
            phrase_list = [choice(x) for x in brawl_list]
            return message.format(r=phrase_list)
        return '`Something wrong with brawl lists. Please check logs for more info`'


def setup(bot):
    bot.add_cog(GoogleBrawl(bot))

"""
Crappy cog for checking overwatch rank
"""

import asyncio
import logging
from time import time

import aiohttp
from bs4 import BeautifulSoup
from discord.ext import commands
from discordbot.models import DiscordUser

logger = logging.getLogger('discordbot.ow')

LINK = "https://playoverwatch.com/en-gb/career/pc/eu/"
HEADERS = {
    'user-agent': ('Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1'), }


class Overwatch2(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.lock = False
        self.timeout = 0
        self.cooldown = 300
        self.futures = []

    @property
    def ow_players(self):
        return (
            DiscordUser.objects
            .exclude(blizzard_id__exact='')
            .values_list('blizzard_id', flat=True)
        )

    @commands.group()
    async def ow(self, ctx):
        if not ctx.invoked_subcommand:
            players = []
            if not ctx.message.mentions:
                players.append(ctx.message.author.id)
            else:
                players.extend([user.id for user in ctx.message.mentions])
            rank_results = list()
            users = DiscordUser.objects.filter(blizard_id__isnull=False).filter(id__in=players)
            if users:
                for user in users:
                    rank = await self.check_ow_rank(user.blizzard_id)
                    rank_results.append(f'{user.display_name} {rank}')

                if len(players) != len(users):
                    rank_results.append("Some players don't have associated Blizzard ID linked")
                await ctx.send('\n'.join(rank_results))
            else:
                pass

    @ow.command()
    async def ladder(self, ctx):
        if not self.lock and time() - self.timeout >= 10:
            try:
                self.lock = True
                tmp_message = await ctx.send('`Loading ladder`')
                ladder = {}
                async with aiohttp.ClientSession() as session:
                    for k in self.ow_players:
                        self.futures.append(
                            self.check_ow_ladder(k, ladder, session))
                    await self.bot.loop.create_task(asyncio.wait(self.futures))
                sorted_ladder = sorted(
                    ladder.items(), key=lambda x: x[1], reverse=True)
                msg = ''
                for player in sorted_ladder:
                    msg += f'    {player[1]} - {player[0]}\n'
                await tmp_message.edit(content=f'<:OSsloth:230773934197440522> \n```xl\nOverwatch rankings\n\n{msg}\n```')
                self.timeout = round(time())
                self.futures.clear()
                await asyncio.sleep(10)
                self.lock = False
            except Exception as ex:
                logger.error(ex)
                self.lock = False
        else:
            cooldown = 10 - round((time() - self.timeout))
            await ctx.send(f"Next update will be available in {cooldown} seconds")

    async def check_ow_rank(self, blizzard_id):
        """OW rank checker"""
        async with aiohttp.ClientSession() as session:
            async with session.get(LINK + blizzard_id) as resp:
                try:
                    text = await resp.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    result = soup.find(
                        "div", {"class": "competitive-rank"}).text
                except Exception as exc:
                    logger.error(exc)
                    result = "Not ranked"
        return result

    async def check_ow_ladder(self, blizzard_id: str, ladder: dict, session: aiohttp.ClientSession):
        try:
            async with session.get(LINK + blizzard_id, headers=HEADERS) as resp:
                text = await resp.text()
                if resp.status == 500:
                    logger.error("Can't load player's page: %s", blizzard_id)
                    return
                soup = BeautifulSoup(text, 'html.parser')
                nickname = blizzard_id.split('-')[0]
                result = soup.find(
                    "div", {"class": "competitive-rank"}).text
                ladder[nickname] = result
        except (AttributeError, TypeError) as ex:
            logger.error(ex)


async def setup(bot):
    await bot.add_cog(Overwatch2(bot))

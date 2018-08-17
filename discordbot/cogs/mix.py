import logging
from collections import deque
from datetime import datetime, timedelta

from discord.ext import commands
from imgurpython import ImgurClient

from discordbot.credentials import IMGUR
from discordbot.models import DiscordPicture, DiscordSettings, Wisdom

from .utils.checks import (admin_command,
                           compare_timestamps, mod_command)
from .utils.db import (get_nickname_cache, get_random_entry,
                       update_display_names)
from .utils.formatters import wisdom_format

logger = logging.getLogger('botLogger')


class Mix(object):

    def __init__(self, bot):
        self.bot = bot
        self.wisdom_history = deque([], maxlen=5)
        self.imgur_update()

    @commands.command(pass_context=True)
    async def mix(self, ctx):
        """Mixes !hb and !wisdom commands"""
        if not ctx.invoked_subcommand:
            wisdom_obj = get_random_entry(Wisdom)
            pic_url = self.get_random_picture()
            if wisdom_obj is not None:
                await self.bot.say('{0}\n{1}'.format(wisdom_obj.text, pic_url))

    @commands.group(pass_context=True)
    async def hb(self, ctx):
        """Нет слов"""
        if not ctx.invoked_subcommand:
            await self.bot.say(self.get_random_picture())

    @hb.command()
    async def update(self):
        """Update pictures table from imgur album"""
        await self.bot.say(self.imgur_update())

    @commands.group(pass_context=True)
    async def wisdom(self, ctx):
        """Спиздануть мудрость клоунов"""
        if not ctx.invoked_subcommand:
            wisdom_obj = get_random_entry(Wisdom)
            if wisdom_obj is not None:
                self.wisdom_history.append(wisdom_obj)
                await self.bot.say(wisdom_obj.text)

    @wisdom.command(pass_context=True)
    @mod_command
    async def add(self, ctx, *, text: str):
        """Добавить новую мудрость клоунов"""
        wisdom_text = text
        Wisdom.objects.create(
            text=wisdom_text,
            date=datetime.now(),
            author_id=ctx.message.author.id
        )
        await self.bot.say('{} added'.format(wisdom_text))

    @wisdom.command(pass_context=True, hidden=True)
    @admin_command
    async def remove(self, ctx, wisdom_id: int):
        """Removes wisdom by given id in ctx"""
        if isinstance(wisdom_id, int):
            entry = Wisdom.objects.filter(id=wisdom_id).delete()
            if entry[0] is not 0:
                await self.bot.say('Wisdom {} removed'.format(wisdom_id))

    def get_random_picture(self):
        """Gets random picture from imgur table and sets new pid based on picture's age"""
        random_pic = DiscordPicture.objects.filter(pid__lt=2).order_by('?').first()
        if random_pic:
            current_pid = random_pic.pid
            new_pid = current_pid + compare_timestamps(random_pic.date)
            DiscordPicture.objects.filter(id=random_pic.id).update(pid=new_pid)
            return random_pic.url
        else:
            DiscordPicture.objects.all().update(pid=0)
            return self.get_random_picture()

    def get_album(self):
        client = ImgurClient(IMGUR['id'], IMGUR['secret'])
        data = client.get_album_images(IMGUR['album'])
        if not data:
            return None
        pictures = {x.link: x.datetime for x in data}
        logger.info('[{0}] Database has been updated with {1} pictures'
                    .format(__name__, len(pictures)))
        logger.info('[{0}] Client limits are {1}/12500'
                    .format(__name__, client.credits['ClientRemaining']))
        return pictures

    def imgur_update(self):
        """Update imgur table"""

        pictures = self.get_album()

        if pictures is None or not isinstance(pictures, dict):
            return 'Imgur album is empty!'

        saved_piclist = DiscordPicture.objects.values_list('url', flat=True)
        for key, value in pictures.items():
            if key not in saved_piclist:
                DiscordPicture.objects.create(url=key, date=value)
        return 'Database has been updated with {} pictures'.format(len(pictures))

    def refresh_wisdom_history(self):
        """Updates current lastwisdom deque if wisdom table changes

        Returns:
            str: Bot message
        """
        temp_ids = [x.id for x in self.wisdom_history]
        self.wisdom_history.clear()
        for item in Wisdom.objects.filter(id__in=temp_ids):
            self.wisdom_history.append(item)
        logger.info('Wisdom deque has been updated')
        return "Wisdom history has been updated"


def setup(bot):
    bot.add_cog(Mix(bot))

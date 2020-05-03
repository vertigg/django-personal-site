import logging
from datetime import datetime

from discord.ext import commands
from django.conf import settings
from imgurpython import ImgurClient

from discordbot.models import DiscordPicture, Wisdom

from .utils.checks import admin_command, compare_timestamps, mod_command
from .utils.db import get_random_entry

logger = logging.getLogger('botLogger')


class Mix(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.imgur_update()

    @commands.command(aliases=['ьшч', 'Mix', 'ЬШЫ', 'MIX', 'Ьшч'])
    async def mix(self, ctx):
        """Mixes !hb and !wisdom commands"""
        if not ctx.invoked_subcommand:
            wisdom_obj = get_random_entry(Wisdom)
            pic_url = self.get_random_picture()
            if wisdom_obj is not None:
                await ctx.send('{0}\n{1}'.format(wisdom_obj.text, pic_url))

    @commands.group()
    async def hb(self, ctx):
        """Returns random picture from HB's Imgur album"""
        if not ctx.invoked_subcommand:
            await ctx.send(self.get_random_picture())

    @hb.command()
    async def update(self, ctx):
        """Update pictures table from imgur album"""
        await ctx.send(self.imgur_update())

    @commands.group()
    async def wisdom(self, ctx):
        """Get random wisdom"""
        if not ctx.invoked_subcommand:
            wisdom_obj = get_random_entry(Wisdom)
            if wisdom_obj is not None:
                await ctx.send(wisdom_obj.text)

    @wisdom.command()
    @mod_command
    async def add(self, ctx, *, text: str):
        """Add new wisdom to database"""
        wisdom_text = text
        Wisdom.objects.create(
            text=wisdom_text,
            date=datetime.now(),
            author_id=ctx.message.author.id
        )
        await ctx.send('{} added'.format(wisdom_text))

    @wisdom.command(hidden=True)
    @admin_command
    async def remove(self, ctx, wisdom_id: int):
        """Removes wisdom by given id in ctx"""
        if isinstance(wisdom_id, int):
            entry = Wisdom.objects.filter(id=wisdom_id).delete()
            if entry[0] is not 0:
                await ctx.send('Wisdom {} removed'.format(wisdom_id))

    def get_random_picture(self):
        """Gets random picture from imgur table and sets new pid based on picture's age"""
        random_pic = DiscordPicture.objects.filter(pid__lt=2) \
            .order_by('?').first()
        if random_pic:
            current_pid = random_pic.pid
            new_pid = current_pid + compare_timestamps(random_pic.date)
            DiscordPicture.objects.filter(id=random_pic.id).update(pid=new_pid)
            return random_pic.url
        else:
            DiscordPicture.objects.all().update(pid=0)
            return self.get_random_picture()

    def get_album(self):
        client = ImgurClient(settings.IMGUR_ID, settings.IMGUR_SECRET)
        data = client.get_album_images(settings.IMGUR_ALBUM)
        if not data:
            return None
        pictures = {x.link: x.datetime for x in data}
        logger.info(
            '[%s] Database has been updated with %d pictures',
            __name__, len(pictures)
        )
        logger.info(
            '[%s] Client limits are %s/12500',
            __name__, client.credits['ClientRemaining']
        )
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


def setup(bot):
    bot.add_cog(Mix(bot))

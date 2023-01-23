import hashlib
import logging
import os
from typing import AnyStr

from aiohttp import ClientSession
from discord import app_commands
from discord.channel import DMChannel, VoiceChannel
from discord.ext import commands
from discord.interactions import Interaction
from discord.threads import Thread
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.timezone import now

from discordbot.models import MixImage, Wisdom

from .utils.checks import is_image_mimetype, mod_command
from .utils.formatters import extract_urls

logger = logging.getLogger('discordbot.mix')


class Mix(commands.Cog):
    wisdom_group = app_commands.Group(name='wisdom', description='Shows deep random wisdoms')

    def __init__(self, bot):
        self.bot = bot

    def _generate_mix_message(self, additional_message: str = None) -> str:
        wisdom_obj = Wisdom.objects.get_random_entry()
        picture_url = MixImage.objects.get_random_entry()
        message_items: list[AnyStr] = []
        if additional_message:
            message_items.append(additional_message)
        if wisdom_obj:
            message_items.append(wisdom_obj.text)
        if picture_url:
            message_items.append(str(picture_url))
        return '\n'.join(message_items)

    @commands.group(aliases=['ьшч', 'Mix', 'ЬШЫ', 'MIX', 'Ьшч', 'мікс', 'міх', 'хіх'])
    async def mix(self, ctx, *, additional_message: str = None):
        """Mixes !hb and !wisdom commands"""
        if not ctx.invoked_subcommand:
            message = self._generate_mix_message(additional_message)
            if isinstance(ctx.channel, (DMChannel, VoiceChannel, Thread)):
                await ctx.channel.send(message)
            else:
                await self.bot.get_channel(settings.DISCORD_MIX_CHANNEL).send(message)

    @mix.command(aliases=['add', 'фвв'])
    @mod_command
    async def __mix_add(self, ctx, *, text: str = None):
        """Add new picture/pictures to mix from given urls or attachments"""
        # Check if urls or attachment provided
        if not any([text, ctx.message.attachments]):
            await ctx.send('No urls or files provided')
            return
        added, errors, urls = 0, [], []
        if text:
            # Extract all urls from given text
            urls.extend(extract_urls(text))
        if ctx.message.attachments:
            urls.extend([x.url for x in ctx.message.attachments])
        for url in urls:
            try:
                # Check content type by calling head for url
                # This could fail for some types of links (e.g. Dropbox)
                async with ClientSession(loop=self.bot.loop) as client:
                    response = await client.head(url)
                    if not is_image_mimetype(response.content_type):
                        errors.append(f'{url} is not a picture')
                        continue

                if response.content_length >= settings.MIX_IMAGE_SIZE_LIMIT:
                    errors.append(
                        f'{url} exceeds allowed filesize limit of '
                        f'{settings.MIX_IMAGE_SIZE_LIMIT_MB} MB'
                    )
                    continue
                # If mimetype is okay - download file and check MD5 hash
                async with ClientSession(loop=self.bot.loop) as client:
                    response = await client.get(url)
                    content = ContentFile(await response.read())

                filename = os.path.basename(url)
                md5 = hashlib.md5(content.read()).hexdigest()

                if MixImage.objects.filter(checksum=md5).exists():
                    errors.append(f'{url} picture already exists in DB')
                    logger.info('%s already exists', filename)
                    continue

                obj = MixImage(date=now(), author_id=ctx.author.id)
                obj.image.save(filename, content, save=True)
                added += 1
            except Exception as exc:
                logger.error(str(exc))
                errors.append(str(exc))
        # Form a message
        message = f'Added {added} image(s) from {len(urls)} url(s)'
        if errors:
            error_messages = '\n'.join(errors)
            message = f'{message}\n```{error_messages}```'
        await ctx.send(message)

    @app_commands.command(name='mix', description='Generate mix image with some text')
    async def mix_generate(self, interaction: Interaction, message: str = None, is_private: bool = False):
        await interaction.response.send_message(self._generate_mix_message(message), ephemeral=is_private)

    @wisdom_group.command(name='generate', description='Generate random wisdom')
    async def wisdom_generate(self, interaction: Interaction):
        await interaction.response.send_message(Wisdom.objects.get_random_entry().text)

    @wisdom_group.command(name='add', description='Adds new wisdom to database')
    @mod_command
    async def wisdom_add(self, interaction: Interaction, text: str):
        if Wisdom.objects.filter(text=text).exists():
            await interaction.response.send_message('Wisdom already exists in db', ephemeral=True)
            return
        Wisdom.objects.create(text=text, author_id=interaction.user.id)
        await interaction.response.send_message(f'{text} added', ephemeral=True)


async def setup(bot):
    await bot.add_cog(Mix(bot))

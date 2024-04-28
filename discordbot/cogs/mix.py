import logging
from typing import AnyStr

from discord import Embed, app_commands
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.interactions import Interaction

from discordbot.cogs.utils.formatters import fix_attachment_url
from discordbot.models import MixImage, Wisdom
from discordbot.tasks import process_mix_urls_async

from .utils.checks import mod_command
from .utils.formatters import build_error_embed, extract_urls

logger = logging.getLogger('discord.mix')


class Mix(commands.Cog):
    wisdom_group = app_commands.Group(name='wisdom', description='Shows deep random wisdoms')
    UPLOAD_FILES_LIMIT = 10

    def __init__(self, bot):
        self.bot = bot

    async def _generate_mix_message(self, additional_message: str = None) -> str:
        wisdom_obj = await Wisdom.objects.aget_random_entry()
        picture_url = await MixImage.objects.aget_random_entry()
        message_items: list[AnyStr] = []
        if additional_message:
            message_items.append(additional_message)
        if wisdom_obj:
            message_items.append(wisdom_obj.text)
        if picture_url:
            message_items.append(str(picture_url))
        return '\n'.join(message_items)

    @commands.group(aliases=['ьшч', 'Mix', 'ЬШЫ', 'MIX', 'Ьшч', 'мікс', 'міх', 'хіх', 'ьіч'])
    async def mix(self, ctx):
        """Mixes !hb and !wisdom commands"""
        if not ctx.invoked_subcommand:
            message = await self._generate_mix_message()
            await ctx.channel.send(message)

    @mix.command(aliases=['add', 'фвв', 'адд'])
    @mod_command
    async def __mix_add(self, ctx: Context, *, content: str = None):
        """Add new picture/pictures to mix from given urls or attachments"""
        urls = set()

        if content:
            urls.update(extract_urls(content))
        if ctx.message.attachments:
            urls.update({fix_attachment_url(x.url) for x in ctx.message.attachments})

        if not urls or len(urls) > self.UPLOAD_FILES_LIMIT:
            if not urls:
                message = "No urls or files were provided"
            else:
                message = f"No more than {self.UPLOAD_FILES_LIMIT} files/links at a time!"
            embed = build_error_embed(title="Mix Upload Error", message=message)
            await ctx.send(embed=embed)
            return

        result, error = await process_mix_urls_async(urls, ctx.author.id)
        if error:
            embed = build_error_embed(title="Mix Upload Error", message="Task timed out!")
            await ctx.send(embed=embed)
            return

        embed = Embed(title="Mix Image Upload")
        left_column, right_column = [], []

        for obj in result:
            left_column.append(f"[{obj.filename}]({obj.url})")
            if obj.valid:
                right_column.append("✅")
            else:
                right_column.append(f"❌ {obj.error_message}")

        embed.add_field(name="File", value="\n".join(left_column), inline=True)
        embed.add_field(name="Result", value="\n".join(right_column), inline=True)

        await ctx.send(embed=embed)

    @app_commands.command(name='mix', description='Generate mix image with some text')
    async def mix_generate(self, interaction: Interaction, message: str = None, is_private: bool = False):
        message = await self._generate_mix_message(message)
        await interaction.response.send_message(message, ephemeral=is_private)

    @wisdom_group.command(name='generate', description='Generate random wisdom')
    async def wisdom_generate(self, interaction: Interaction):
        obj = await Wisdom.objects.aget_random_entry()
        await interaction.response.send_message(obj.text)

    @wisdom_group.command(name='add', description='Adds new wisdom to database')
    @mod_command
    async def wisdom_add(self, interaction: Interaction, text: str):
        if await Wisdom.objects.filter(text=text).aexists():
            await interaction.response.send_message('Wisdom already exists in db', ephemeral=True)
            return
        await Wisdom.objects.acreate(text=text, author_id=interaction.user.id)
        await interaction.response.send_message(f'{text} added', ephemeral=True)


async def setup(bot):
    await bot.add_cog(Mix(bot))

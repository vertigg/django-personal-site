import logging
from typing import Union

import wikipedia
from discord import Color, Embed
from discord.ext import commands
from django.template.defaultfilters import truncatechars
from wikipedia.exceptions import DisambiguationError, PageError

from discordbot.cogs.utils.checks import admin_command

logger = logging.getLogger('discordbot.wiki')


class Wikipedia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_embed_color = Color(0x00910b)
        wikipedia.set_lang('uk')

    @commands.command()
    async def wiki(self, ctx, *, term: str):
        """Википедия в Дискорде, не отходя от кассы"""
        await ctx.send(embed=self.get_search_result(term))

    @commands.command(hidden=True)
    @admin_command
    async def set_wiki_language(self, ctx, *, language_code: str):
        if language_code in wikipedia.languages().keys():
            wikipedia.set_lang(language_code)
            await ctx.send(f'Wiki language changed to {language_code}', delete_after=5)
        else:
            await ctx.send('Invalid language code', delete_after=5)

    def truncate_summary(self, summary: str) -> str:
        return summary if len(summary) < 1000 else truncatechars(summary, 700)

    def get_thumbnail_image(self, images: list[str]) -> Union[str, None]:
        if thumbnails := [i for i in images if i.endswith(('jpeg', 'jpg'))]:
            return thumbnails[0]
        return None

    def get_search_result(self, term: str) -> Embed:
        try:
            page = wikipedia.page(term)
            embed = Embed(
                url=page.url,
                title=page.title,
                colour=self.default_embed_color,
                description=self.truncate_summary(page.summary)
            )
            if thumbnail := self.get_thumbnail_image(page.images):
                embed.set_thumbnail(url=thumbnail)
            return embed
        except DisambiguationError as exc:
            return Embed(
                title=f"Too many results for {exc.title}",
                colour=self.default_embed_color,
                description=self.truncate_summary(', '.join(exc.options))
            )
        except PageError as exc:
            title = exc.title if hasattr(exc, 'title') else exc.pageid
            return Embed(
                title=f"No results for {title}",
                colour=self.default_embed_color,
                description=self.truncate_summary(exc.__unicode__())
            )


async def setup(bot):
    await bot.add_cog(Wikipedia(bot))

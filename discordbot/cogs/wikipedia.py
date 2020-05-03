import logging

import wikipedia
from discord import Color, Embed
from discord.ext import commands
from django.template.defaultfilters import truncatechars
from wikipedia.exceptions import DisambiguationError, PageError

logger = logging.getLogger('discordbot.wiki')


class Wikipedia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        wikipedia.set_lang('ru')

    @commands.group()
    async def wiki(self, ctx, *, search: str):
        """Википедия в Дискорде, не отходя от кассы"""
        if not ctx.invoked_subcommand:
            await ctx.send(embed=self.get_search_result(search))

    def truncate_summary(self, summary: str):
        return summary if len(summary) < 1000 else truncatechars(summary, 700)

    def get_thumbnail_image(self, images: list):
        if images:
            jpeg_images = list(filter(
                lambda image: any(x in image for x in ['jpg', 'jpeg']), images))
            if jpeg_images:
                return jpeg_images[0]
        return None

    def get_search_result(self, request):
        try:
            page = wikipedia.page(request)
            embed = Embed(
                url=page.url,
                title=page.title,
                colour=Color(0x00910b),
                description=self.truncate_summary(page.summary))
            thumbnail = self.get_thumbnail_image(page.images)
            if thumbnail:
                embed.set_thumbnail(url=thumbnail)
            return embed
        except DisambiguationError as exc:
            return Embed(
                title=f"Too many results for {exc.title}",
                colour=Color(0x00910b),
                description=self.truncate_summary(', '.join(exc.options))
            )
        except PageError as exc:
            title = exc.title if hasattr(exc, 'title') else exc.pageid
            return Embed(
                title=f"No results for {title}",
                colour=Color(0x00910b),
                description=self.truncate_summary(exc.__unicode__())
            )


def setup(bot):
    bot.add_cog(Wikipedia(bot))

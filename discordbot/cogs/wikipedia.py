import logging

import wikipedia
from discord.ext import commands

logger = logging.getLogger("botLogger")


class Wikipedia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        wikipedia.set_lang('ru')

    @commands.group()
    async def wiki(self, ctx, *, search: str):
        """Википедия в Дискорде, не отходя от кассы"""
        # article = str(ctx.message.content).replace('!wiki ', '')
        if not ctx.invoked_subcommand:
            try:
                await ctx.send('`{}`'.format(self.get_article(search)[0]))
            except Exception as e:
                logger.error(e)

    def get_article(self, article):
        try:
            wikiresult = wikipedia.summary(article).split('\n')[0]
            wikilink = wikipedia.page(article).url
        except wikipedia.exceptions.DisambiguationError as e:
            wikiresult = str(str(e).split(': \n')[1].split('\n')).strip('[]')
            if len(wikiresult) >= 250:
                wikiresult = 'Слишком много результатов, попробуй запрос поточнее'
            wikilink = 'Слишком много результатов чтобы выдать ссылку, попробуй поточнее'
        except Exception as ex:
            wikiresult = str(ex)
            wikilink = str(ex)
        return wikiresult, wikilink


def setup(bot):
    bot.add_cog(Wikipedia(bot))

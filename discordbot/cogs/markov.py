import logging

import pandas as pd
import pytz
from discord.errors import HTTPException
from discord.ext import commands
from django.db.models.functions import Length
from markovify import Text

from discordbot.models import MarkovText

from .utils.checks import admin_command
from .utils.formatters import clean_text

logger = logging.getLogger('botLogger.Markov')


class Markov(commands.Cog):

    max_sentences = 20

    def __init__(self, bot):
        self.bot = bot
        self._excluded_ids = [223837667186442240, 359297047830069251]
        self.markov_texts = self._get_cached_texts()
        self.channel_locks = dict.fromkeys(self.markov_texts, False)

    def _get_cached_texts(self):
        return {x[0]: Text(x[1]) for x in list(
            MarkovText.objects
            .annotate(text_length=Length('text'))
            .filter(text_length__gte=1)
            .values_list('key', 'text')
            .distinct()
        )}

    def _clean_up_markov_text(self, df: pd.DataFrame):
        """Processes message dataframe into markov chain clean text"""
        df = df[~df.author_id.isin(self._excluded_ids)]  # Remove messages from certain people
        df = df.dropna(subset=['content'])  # Remove messages without text content
        df = df[~df.content.str.startswith('!')]  # Remove messages that starts with command_prefix
        df['content'] = df.content.apply(clean_text)
        df = df[~df.content.eq('')]
        return ' '.join(df.content).strip()

    async def _get_history(self, ctx, limit=None, after=None):
        return await ctx.channel.history(limit=limit, after=after).flatten()

    async def _update_from_command(self, ctx):
        """Creates new MarkovText object if `markov` command was invoked and no
        text is available for generating sentences

        Args:
            ctx (Context): Message context
        """
        await ctx.send('It seems that there is not text for this channel! '
                       'Building text object')
        await ctx.invoke(self.bot.get_command('markov update'))
        await ctx.send('Markov text object is ready for this channel! '
                       'To use it - type !markov <sentences>')

    @commands.group(invoke_without_command=True)
    async def markov(self, ctx, *, sentences: int = 5):
        """
        Generates sentences from current text channel using Markov chain algorithm
        """
        if not self.channel_locks.get(ctx.channel.id, False):
            text = self.markov_texts.get(ctx.channel.id, None)
            if not text:
                return await self._update_from_command(ctx)
            sentences_count = sentences if sentences <= self.max_sentences else self.max_sentences
            if not ctx.invoked_subcommand and text:
                text = ' '.join([text.make_short_sentence(250, tries=100) for x
                                 in range(sentences_count)])
                await ctx.send(text)
        else:
            await ctx.send('Chat update in progress')

    @markov.command()
    @admin_command
    async def update(self, ctx):
        """
        Command used for updating MarkovText object for current text channel.
        Can be invoked by admin user only 
        """
        channel_id = ctx.channel.id
        self.channel_locks[channel_id] = True
        try:
            obj = MarkovText.objects.filter(key=channel_id).first()
            if channel_id in self.markov_texts.keys() and obj and obj.last_update:
                last_update = obj.last_update.replace(tzinfo=None)
                logger.info(
                    'Updating markov text since %s for %s channel',
                    last_update, channel_id
                )
                messages = await self._get_history(ctx, after=last_update)
            else:
                logger.info('Downloading full chat history for %s', channel_id)
                messages = await self._get_history(ctx)
            if messages:
                messages_df = pd.DataFrame([{
                    'message_id': x.id,
                    'author_id': x.author.id,
                    'content': x.content,
                    'created_at': x.created_at,
                } for x in messages]).astype({'created_at': 'datetime64'})
                new_text = self._clean_up_markov_text(messages_df)
                if new_text:
                    obj, _ = MarkovText.objects.get_or_create(key=channel_id)
                    obj.text = f'{new_text} {obj.text}'
                    obj.last_update = (messages_df.created_at
                                       .dt.tz_localize(pytz.UTC)
                                       .dt.to_pydatetime().max())
                    obj.save()
                    self.markov_texts[channel_id] = Text(obj.text)
                    message = (
                        f'Markov text is now `{len(obj.text)}` characters for '
                        f'channel `{channel_id}`'
                    )
                    logger.info(message)
                    await ctx.send(message)
                else:
                    logger.info('There are no messages to add for %d', channel_id)
        finally:
            self.channel_locks[channel_id] = False

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(error, 'original') and isinstance(error.original, HTTPException):
            if ctx.command.name == 'markov':
                await ctx.send(f"Can't generate text with length of "
                               f"{ctx.kwargs.get('sentences')}")


def setup(bot):
    bot.add_cog(Markov(bot))

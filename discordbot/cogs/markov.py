import logging
import re
import string

import pandas as pd
import pytz
from discord.errors import HTTPException
from discord.ext import commands
from markovify import Text

from discordbot.models import MarkovText

from .utils.checks import admin_command

logger = logging.getLogger('botLogger.Markov')


class Markov(commands.Cog):

    max_sentences = 20
    http_regex = re.compile(
        r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
    mention_regex = re.compile(r'\<\@\d+\>')
    emoji_regex = re.compile(r'\<:\w+:\d+\>')
    multiple_spaces_regex = re.compile(r'\s+')

    regexes = [http_regex, mention_regex, emoji_regex, multiple_spaces_regex]

    def __init__(self, bot):
        self.bot = bot
        self.markov_model = MarkovText.objects.get(key='default')
        self.markov_text = Text(self.markov_model.text)
        self._locked = False
        self._excluded_ids = [223837667186442240, 359297047830069251]
        # TODO: Add additional field for id of text channel
        self._allowed_channels = [178976406288465920, 465820028718153738]

    def _add_punctuation(self, text):
        if not any([text.endswith(y) for y in string.punctuation]) and len(text) > 1:
            return f'{text}.'
        return text

    def _clean_message(self, text):
        """Cleans up discord message from mentions, links and emojis"""
        for regex_pattern in self.regexes:
            text = regex_pattern.sub(' ', text.strip())
        return self._add_punctuation(text).strip().capitalize()

    def _clean_up_markov_text(self, df: pd.DataFrame):
        """Processes message dataframe into markov chain clean text"""
        df = df[~df.author_id.isin(self._excluded_ids)]  # Remove messages from certain people
        df = df.dropna(subset=['content'])  # Remove messages without text content
        df = df[~df.content.str.contains(r'^!')]  # Remove messages that starts with command_prefix
        df['content'] = df.content.apply(self._clean_message)
        df = df[~df.content.eq('')]
        return ' '.join(df.content).strip()

    @commands.group(invoke_without_command=True)
    async def markov(self, ctx, *, sentences: int = 3):
        if not self._locked:
            sentences_count = sentences if sentences <= self.max_sentences else self.max_sentences
            if not ctx.invoked_subcommand:
                text = ' '.join([self.markov_text.make_short_sentence(250, tries=100) for x in range(sentences_count)])
                await ctx.send(text)
        else:
            await ctx.send('Chat update in progress')

    @markov.command()
    @admin_command
    async def update(self, ctx):
        if ctx.channel.id in self._allowed_channels:
            self._locked = True
            try:
                self.markov_model.refresh_from_db()
                if self.markov_model.last_update:
                    last_update = self.markov_model.last_update.replace(tzinfo=None)
                    logger.info(f'Updating markov text since {last_update}')
                    messages = await ctx.channel.history(limit=None, after=last_update).flatten()
                else:
                    logger.info('Downloading chat history')
                    messages = await ctx.channel.history(limit=None).flatten()
                if messages:
                    messages_df = pd.DataFrame([{
                        'message_id': x.id,
                        'author_id': x.author.id,
                        'content': x.content,
                        'created_at': x.created_at,
                    } for x in messages]).astype({'created_at': 'datetime64'})
                    new_text = self._clean_up_markov_text(messages_df)
                    if new_text:
                        self.markov_model.text = f'{new_text} {self.markov_model.text}'
                        self.markov_model.last_update = (messages_df.created_at
                                                         .dt.tz_localize(pytz.UTC)
                                                         .dt.to_pydatetime().max())
                        self.markov_model.save()
                        self.markov_text = Text(self.markov_model.text)
                        logger.info(f'Markov text has been updated with {len(new_text)} characters')
                    else:
                        logger.info('There are no messages to add')
            finally:
                self._locked = False

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(error, 'original') and isinstance(error.original, HTTPException):
            if ctx.command.name == 'markov':
                await ctx.send(f"Can't generate text with length of {ctx.kwargs.get('sentences')}")


def setup(bot):
    bot.add_cog(Markov(bot))
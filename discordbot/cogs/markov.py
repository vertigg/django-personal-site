import logging
from datetime import datetime

import pandas as pd
from discord import app_commands
from discord.errors import HTTPException
from discord.ext import commands, tasks
from discord.interactions import Interaction
from django.db.models.functions import Length
from markovify import Text

from discordbot.config import settings
from discordbot.models import MarkovText

from .utils.checks import admin_command, text_channels_only
from .utils.exceptions import UnavailableChannelError
from .utils.formatters import clean_text

logger = logging.getLogger('discordbot.markov')


class Markov(commands.Cog):

    max_sentences = 20

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.markov_texts = self._get_cached_texts()
        self.channel_locks = dict.fromkeys(self.markov_texts, False)
        self.update_text_caches.start()

    def cog_unload(self):
        self.update_text_caches.cancel()
        return super().cog_unload()

    async def __update(self, ctx, channel_id: int = None):
        """Main MarkovText update function. Depending on provided arguments will
        update MarkovText instance or create a new one for specific channel ID
        (for given channel_id or ctx.channel.id)

        Args:
            ctx (Context|None): Current message context if available
            channel_id (int|None): Specific channel ID, if passed as None it will
            fallback to ctx.channel.id if ctx is available
        Raises:

        """
        obj = MarkovText.objects.filter(key=channel_id).first()
        new_text = None
        message = None
        if channel_id in self.markov_texts.keys() and obj and obj.last_update:
            logger.info(
                'Updating markov text since %s for %s channel',
                obj.last_update, channel_id
            )
            messages = await self._get_history(channel_id, ctx=ctx, after=obj.last_update)
        else:
            logger.info('Downloading full chat history for %s', channel_id)
            messages = await self._get_history(channel_id, ctx=ctx)
        if messages:
            messages_df = pd.DataFrame([{
                'message_id': message.id,
                'author_id': message.author.id,
                'content': message.content,
                'created_at': message.created_at,
            } for message in messages])
            new_text = self._clean_up_markov_text(messages_df)
            if new_text:
                obj, _ = MarkovText.objects.get_or_create(key=channel_id)
                obj.text = f'{new_text} {obj.text}'
                obj.last_update = messages_df.created_at.dt.to_pydatetime().max()
                obj.save()
                self.markov_texts[channel_id] = Text(obj.text)
                message = (
                    f'Markov text is now `{len(obj.text)}` characters for '
                    f'channel `{channel_id}`'
                )
                logger.info(message)
                if ctx:
                    await ctx.send(message)

        if not message or not new_text:
            message = f'There are no messages to add for `{channel_id}`'
            logger.info(message)
            if ctx:
                await ctx.send(message)

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
        df = df[~df.author_id.isin(settings.MARKOV_EXCLUDE_IDS)]  # Remove messages from certain people
        df = df.dropna(subset=['content'])  # Remove messages without text content
        df = df[~df.content.str.startswith('!')]  # Remove messages that starts with command_prefix
        df['content'] = df.content.apply(clean_text)
        df = df[~df.content.eq('')]
        return ' '.join(df.content).strip()

    async def _get_history(self, channel_id: int, ctx=None,
                           limit: int = None, after: datetime = None) -> list:
        """Shortcut for history retrieval. History can be retrieved either by
        providing context (ctx) or channel ID.

        Args:
            ctx (Context, optional): Current message context. Defaults to None.
            channel_id: Discord Channel ID. Bot must have
                permissions to read that channel. Defaults to None.
            limit: Limits the number of messages we want to retrieve.
                Defaults to None.
            after: Optional datetime after which we want to retrieve messages.
                Defaults to None.

        Raises:
            UnavailableChannelError: In case of trying to get history from channel
            restricted for current bot

        Returns:
            list[discord.Message]: List of instances of discord.Message
        """

        try:
            history = self.bot.get_channel(channel_id).history(limit=limit, after=after)
            return [message async for message in history]
        except AttributeError as exc:
            message = f'Bot does not have access to `{channel_id}` channel'
            if ctx:
                await ctx.send(message)
            raise UnavailableChannelError(message) from exc

    async def _update_from_command(self, ctx):
        """Creates new MarkovText object if `markov` command was invoked and no
        text is available for generating sentences. Notifies users in current
        channel and invokes `markov update` with current context

        Args:
            ctx (Context): Message context
        """
        await ctx.send('It seems that there is no text for this channel! '
                       'Building text object')
        await ctx.invoke(self.bot.get_command('markov update'))
        await ctx.send('Markov text object is ready for this channel! '
                       'To use it - type !markov <sentences count>')

    @commands.group(invoke_without_command=True)
    @text_channels_only
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

    @app_commands.command(name='markov', description='Generate markov text for current chat room')
    async def markov_interaction(self, interaction: Interaction, sentences: int = 5):
        if interaction.channel.id not in settings.MARKOV_ALLOWED_CHANNELS:
            return await interaction.response.send_message('Markov command can be used only in general channel')
        if not self.channel_locks.get(interaction.channel_id, False):
            await interaction.response.defer(thinking=True)
            text = self.markov_texts.get(interaction.channel_id)
            sentences_count = sentences if sentences <= self.max_sentences else self.max_sentences
            result = ' '.join([text.make_short_sentence(250, tries=100) for _ in range(sentences_count)])
            await interaction.followup.send(result)
        else:
            await interaction.response.send_message('Update in progress, please try later', ephemeral=True)

    @markov.command()
    @admin_command
    @text_channels_only
    async def update(self, ctx, channel_id: int = None):
        """
        Command used for updating MarkovText object for current text channel.
        Can be invoked by admin user only
        """
        channel_id = ctx.channel.id if not channel_id and ctx else channel_id
        self.channel_locks[channel_id] = True
        try:
            await self.__update(ctx, channel_id)
        finally:
            self.channel_locks[channel_id] = False

    @markov.command()
    @admin_command
    async def refresh_caches(self, ctx):
        """
        Admin command for refreshing markov text caches
        """
        self.markov_texts = self._get_cached_texts()
        self.channel_locks = dict.fromkeys(self.markov_texts, False)
        await ctx.send('Markov text caches refreshed', delete_after=5)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(error, 'original') and isinstance(error.original, HTTPException):
            if ctx.command.name == 'markov':
                await ctx.send(f"Can't generate text with length of "
                               f"{ctx.kwargs.get('sentences')}")

    @tasks.loop(hours=24, reconnect=True)
    async def update_text_caches(self):
        """
        Periodically updates available cached objects with new messages
        """
        await self.bot.wait_until_ready()
        for channel_id in self.markov_texts.keys():
            try:
                await self.__update(ctx=None, channel_id=channel_id)
            except Exception as exc:
                logger.error('Can not update %d. %s', channel_id, str(exc))


async def setup(bot):
    await bot.add_cog(Markov(bot))

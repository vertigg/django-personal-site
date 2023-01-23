import logging
import os

import discord
from discord.ext.commands import Bot

from apps import setup_django

logger = logging.getLogger('discordbot')


class TonyBot(Bot):
    cog_names: list[str] = ['admin', 'general', 'markov', 'mix', 'wikipedia']

    def __init__(self):
        setup_django()
        self._token = None
        super().__init__(
            command_prefix='!',
            description='Super duper halal bot for clowans. List of commands below',
            intents=self.get_bot_intents()
        )

    @property
    def token(self):
        if not self._token:
            from django.conf import settings
            self._token = settings.DISCORD_TEST_TOKEN if os.getenv('DISCORD_TEST', None) \
                else settings.DISCORD_BOT_TOKEN
        return self._token

    def get_bot_intents(self) -> discord.Intents:
        intents = discord.Intents.default()
        intents.members = True
        intents.messages = True
        intents.message_content = True
        return intents

    async def load_local_extensions(self) -> None:
        logger.info("Loading extensions...")
        for cog in self.cog_names:
            try:
                await bot.load_extension("cogs." + cog)
                logger.info("'%s' extension loaded", cog)
            except (AttributeError, ImportError) as ex:
                logger.error("%s", ex)

    async def resync_command_tree(self):
        await self.tree.sync()

    async def setup_hook(self) -> None:
        await self.load_local_extensions()
        await self.resync_command_tree()

    async def on_ready(self):
        from discordbot.models import DiscordSettings
        game = discord.Game(DiscordSettings.get('game', default='No game'))
        await bot.change_presence(activity=game)
        logger.info('Logged in as %s:%s', bot.user.name, bot.user.id)

    async def on_message_delete(self, message):
        logger.info(
            'Message deleted: Author %s, Content "%s", Attachments: %s',
            message.author.id, message.content, len(message.attachments)
        )
        if message.attachments:
            logger.info(', '.join([att.url for att in message.attachments]))


bot = TonyBot()
bot.run(bot.token, reconnect=True)

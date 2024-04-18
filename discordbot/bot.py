import logging
from functools import cached_property

import discord
from discord.ext.commands import Bot

from discordbot.config import settings

logger = logging.getLogger('discord.tonybot')


class TonyBot(Bot):
    cog_names: list[str] = ['admin', 'general', 'markov', 'mix', 'wikipedia']

    def __init__(self):
        super().__init__(
            command_prefix='!',
            description='Super duper halal bot for clowans. List of commands below',
            intents=self.get_bot_intents(),
            owner_ids=settings.OWNER_IDS
        )

    @cached_property
    def token(self):
        if settings.TEST:
            return settings.TEST_TOKEN
        return settings.BOT_TOKEN

    def get_bot_intents(self) -> discord.Intents:
        intents = discord.Intents.default()
        intents.members = True
        intents.messages = True
        intents.message_content = True
        intents.presences = True
        return intents

    async def load_local_extensions(self) -> None:
        logger.info("Loading extensions...")
        for cog in self.cog_names:
            try:
                await self.load_extension("discordbot.cogs." + cog)
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
        name = await DiscordSettings.aget('game')
        await self.change_presence(activity=discord.Game(name))
        logger.info('Logged in as %s:%s', self.user.name, self.user.id)

    async def on_presence_update(self, _, after):
        if after.id == 138275152415817728 and after.status == discord.Status.online:
            logger.info('Inked went online')

    async def on_message_delete(self, message: discord.Message):
        logger.info(
            'Message deleted: Author %s, Content "%s", Attachments: %s',
            message.author.id, message.content, len(message.attachments)
        )
        if message.attachments:
            logger.info(', '.join([att.url for att in message.attachments]))

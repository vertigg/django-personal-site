import logging

from discord import app_commands
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui import Modal, TextInput

from discordbot.cogs.utils.checks import validate_poe_profile
from discordbot.cogs.utils.exceptions import (
    DuplicatedProfileException, PrivateProfileException
)
from discordbot.models import DiscordUser
from poe.tasks import remove_related_characters

logger = logging.getLogger('discord.poe')


class PathOfExileCog(commands.Cog):
    poe_group = app_commands.Group(name='poe', description='Path of Exile commands')

    def __init__(self, bot):
        self.bot = bot

    @poe_group.command(name='account', description='Add or remove your PoE account from private ladder')
    async def account(self, interaction: Interaction):
        if user := await DiscordUser.objects.filter(id=interaction.user.id).afirst():
            return await interaction.response.send_modal(AccountModal(user=user))
        await interaction.response.send_message('Local user not found, please try again later', ephemeral=True)


class AccountModal(Modal, title='Private PoE Ladder Account'):
    def __init__(self, *args, user: DiscordUser = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user = user
        self.text_input = TextInput(
            label='Account Name',
            placeholder=user.poe_profile,
            max_length=128,
            required=False
        )
        self.add_item(self.text_input)

    async def on_submit(self, interaction: Interaction, /) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        if self.text_input.value == self.user.poe_profile:
            return await interaction.followup.send('No changes were made')
        profile = await validate_poe_profile(self.text_input.value)
        self.user.poe_profile = profile
        await self.user.asave(update_fields=['poe_profile'])
        if profile is None:
            remove_related_characters.delay(discord_id=self.user.id)
            return await interaction.followup.send('Profile successfully removed!', ephemeral=True)
        await interaction.followup.send('Profile successfully added!', ephemeral=True)

    async def on_error(self, interaction: Interaction, error: Exception, /) -> None:
        if isinstance(error, (DuplicatedProfileException, PrivateProfileException)):
            return await interaction.followup.send(str(error), ephemeral=True)
        logger.error(error)
        return await interaction.followup.send('Something went wrong', ephemeral=True)


async def setup(bot):
    await bot.add_cog(PathOfExileCog(bot))

import logging

import msgspec
from discord import Embed, app_commands
from discord.ext import commands
from discord.interactions import Interaction

from discordbot.cogs.utils.formatters import send_error_embed
from discordbot.cogs.utils.http import async_httpx_request
from discordbot.schemas import MajorOrder

logger = logging.getLogger('discord.helldivers')


class Helldivers(commands.Cog):
    war_id = 801  # TODO: find out what the hell is this value
    url = f"https://api.live.prod.thehelldiversgame.com/api/v2/Assignment/War/{war_id}"

    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.decoder = msgspec.json.Decoder(list[MajorOrder])

    @app_commands.command(name='orders', description='Fetch any major orders for HD2')
    async def orders_command(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        resp, err = await async_httpx_request("GET", self.url, headers={
            "Accept-Language": "en-US"
        })

        if err:
            logger.error(err)
            return await send_error_embed(interaction, "Can't fetch new data at this time")

        tasks = self.decoder.decode(resp.content)

        embed = Embed(title="Major Orders")

        for task in tasks:
            embed.add_field(name="Order", value=str(task))

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Helldivers(bot))

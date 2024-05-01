import logging

from discord import Embed, app_commands
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.interactions import Interaction
from pydantic import TypeAdapter, ValidationError

from discordbot.cogs.utils.checks import admin_command
from discordbot.cogs.utils.formatters import send_error_embed
from discordbot.cogs.utils.http import async_httpx_request
from discordbot.schemas import MajorOrder

logger = logging.getLogger('discord.helldivers')


class Helldivers(commands.Cog):
    war_id: int = 801  # TODO: find out what the hell is this value
    thumbnail_url: str = "https://i.imgur.com/GDzDdJB.jpg"

    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.adapter = TypeAdapter(list[MajorOrder])

    @property
    def default_headers(self) -> dict[str, str]:
        return {"Accept-Language": "en-US"}

    @property
    def orders_endpoint(self) -> str:
        return f"https://api.live.prod.thehelldiversgame.com/api/v2/Assignment/War/{self.war_id}"

    @commands.command(hidden=True)
    @admin_command
    async def change_war_id(self, ctx: Context, *, war_id: int):
        self.war_id = war_id
        await ctx.send(f"Updated War ID to {war_id}", delete_after=5)

    @app_commands.command(name='orders', description='Fetch any major orders for HD2')
    async def orders_command(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        resp, err = await async_httpx_request("GET", self.orders_endpoint, headers=self.default_headers)

        if err:
            logger.error(err)
            return await send_error_embed(interaction, "Can't fetch orders at this time")

        try:
            tasks = self.adapter.validate_json(resp.content)
        except ValidationError:
            return await send_error_embed(interaction, "Can't parse HD2 server response")

        embed = Embed(title="Major Orders").set_thumbnail(url=self.thumbnail_url)

        for task in tasks:
            embed.add_field(name='', value=str(task))

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Helldivers(bot))

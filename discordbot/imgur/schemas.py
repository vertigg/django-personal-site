from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel

from discordbot.config import settings


class ImgurTokenPair(BaseModel):
    refresh_token: str
    access_token: str
    expires_at: datetime

    async def save(self):
        from discordbot.models import DiscordSettings
        if self.refresh_token:
            await DiscordSettings.set(
                settings.IMGUR_REFRESH_TOKEN_DB_KEY, self.refresh_token
            )

    @property
    def is_valid(self) -> bool:
        return datetime.now() < self.expires_at

    @classmethod
    def validate(cls, value: Any):
        value['expires_at'] = datetime.now() + timedelta(seconds=3580)
        return super().validate(value)

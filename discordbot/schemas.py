from datetime import timedelta

from django.utils.text import Truncator
from humanize import precisedelta
from pydantic import AnyHttpUrl, BaseModel, Field


class ProcessedMixImage(BaseModel):
    url: AnyHttpUrl
    valid: bool
    filename: str = None
    errors: list[str] = []

    @property
    def name(self) -> str:
        if not self.filename:
            return 'image'
        return self.filename if len(self.filename) < 50 else Truncator(self.name).chars(50)

    @property
    def error_message(self) -> str:
        return ', '.join(self.errors)

    def add_error_message(self, message: str):
        self.errors.append(message)


class OrderReward(BaseModel):
    amount: int

    def __str__(self) -> str:
        return f"Reward: **{self.amount}** 🏅"


class OrderBody(BaseModel):
    type: int
    title: str = Field(alias="overrideTitle")
    brief: str = Field(alias="overrideBrief")
    description: str = Field(alias="taskDescription")
    reward: OrderReward

    def __str__(self) -> str:
        return f"**{self.description}**\n\n{self.brief}"


class MajorOrder(BaseModel):
    expires_in: int = Field(alias="expiresIn")
    setting: OrderBody

    def __str__(self) -> str:
        expires_delta = timedelta(seconds=self.expires_in)
        expires_msg = precisedelta(expires_delta, minimum_unit="hours", format="%0.0f")
        return "\n\n".join([
            str(self.setting),
            str(self.setting.reward),
            f"Order expires in: **{expires_msg}**"
        ])

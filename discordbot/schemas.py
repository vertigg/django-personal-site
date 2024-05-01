from datetime import timedelta

import msgspec
from django.utils.text import Truncator
from humanize import precisedelta


class ProcessedMixImage(msgspec.Struct):
    url: str
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


class OrderReward(msgspec.Struct):
    amount: int

    def __str__(self) -> str:
        return f"Reward: **{self.amount}** 🏅"


class OrderBody(msgspec.Struct):
    type: int
    title: str = msgspec.field(name="overrideTitle")
    brief: str = msgspec.field(name="overrideBrief")
    description: str = msgspec.field(name="taskDescription")
    reward: OrderReward

    def __str__(self) -> str:
        return f"**{self.description}**\n\n{self.brief}"


class MajorOrder(msgspec.Struct):
    expires_in: int = msgspec.field(name="expiresIn")
    setting: OrderBody

    def __str__(self) -> str:
        expires_delta = timedelta(seconds=self.expires_in)
        expires_msg = precisedelta(expires_delta, minimum_unit="hours", format="%0.0f")
        return "\n\n".join([
            str(self.setting),
            str(self.setting.reward),
            f"Order expires in: **{expires_msg}**"
        ])

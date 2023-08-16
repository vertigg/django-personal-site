from datetime import datetime
from enum import Enum

from pydantic import AnyUrl, BaseModel, Field


class CharacterSchema(BaseModel):
    name: str
    league: str
    level: int
    expired: bool | None = False
    class_name: str = Field(alias='class')

    class Config:
        allow_population_by_field_name = True


class LeagueSchema(BaseModel):
    name: str = Field(alias='id')
    realm: str | None
    url: AnyUrl
    start_date: datetime | None = Field(alias='startAt')
    end_date: datetime | None = Field(alias='endAt')


class SocketedGemSchema(BaseModel):
    name: str = Field(alias='typeLine')
    icon: AnyUrl | None
    is_support: bool = Field(alias='support', default=False)

    @property
    def is_active(self):
        return not self.is_support


class PoBDataSchema(BaseModel):
    life: int = Field(alias='Life')
    es: int = Field(alias='EnergyShield')
    combined_dps: float = Field(alias='CombinedDPS')


class PoBFileType(str, Enum):
    TREE = 'tree'
    ITEMS = 'items'

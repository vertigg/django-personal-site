from datetime import datetime

from pydantic import AnyUrl, BaseModel, Field


class CharacterSchema(BaseModel):
    name: str
    league: str
    level: int
    expired: bool | None = False
    experience: int
    class_id: int = Field(alias='classId')
    class_name: str = Field(alias='class')
    ascendancy_id: int = Field(alias='ascendancyClass')

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

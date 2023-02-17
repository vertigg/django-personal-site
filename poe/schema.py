from pydantic import BaseModel, Field


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

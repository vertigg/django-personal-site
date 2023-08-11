from pydantic import BaseSettings


class PoELocalSettings(BaseSettings):
    LADDER_METADATA_MIN_LEVEL: int = 90
    POB_RUNTIME_PATH: str = None
    POB_SOURCE_PATH: str = None
    TEMP_FOLDER: str = '/tmp/'


settings = PoELocalSettings()

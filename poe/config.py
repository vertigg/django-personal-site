from pydantic import BaseSettings


class PoELocalSettings(BaseSettings):
    POB_RUNTIME_PATH: str = None
    POB_SOURCE_PATH: str = None
    TEMP_FOLDER: str = '/tmp/'


settings = PoELocalSettings()

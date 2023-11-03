from pydantic import BaseSettings


class DiscordBotLocalSettings(BaseSettings):
    BOT_TOKEN: str
    TEST_TOKEN: str = None
    TEST: bool = False
    MIX_IMAGE_SIZE_LIMIT_MB: int = 8
    MIX_IMAGE_SIZE_LIMIT: int = MIX_IMAGE_SIZE_LIMIT_MB * 1024 * 1024  # 8 Megabytes
    MARKOV_ALLOWED_CHANNELS: list[int] = [178976406288465920, 469130152882733061, 767677709639745537]
    MARKOV_EXCLUDE_IDS: list[int] = [223837667186442240, 345296059712405505]
    OWNER_IDS: set[int] = {121371550405361664}

    IMGUR_CLIENT_ID: str
    IMGUR_CLIENT_SECRET: str
    IMGUR_ALBUM_HASH: str
    IMGUR_REFRESH_TOKEN_DB_KEY: str = 'imgur_refresh_token'

    class Config:
        env_prefix = 'DISCORD_'
        env_file = '.env'


settings = DiscordBotLocalSettings()

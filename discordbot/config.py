from pydantic import BaseSettings


class DiscordBotLocalSettings(BaseSettings):
    BOT_TOKEN: str
    TEST_TOKEN: str = None
    TEST: bool = False
    MIX_CHANNEL: int = 927203296685477888
    MIX_IMAGE_SIZE_LIMIT_MB: int = 8
    MIX_IMAGE_SIZE_LIMIT: int = MIX_IMAGE_SIZE_LIMIT_MB * 1024 * 1024  # 8 Megabytes
    MARKOV_ALLOWED_CHANNELS: list[int] = [178976406288465920, 469130152882733061, 767677709639745537]

    class Config:
        env_prefix = 'DISCORD_'
        env_file = '.env'


settings = DiscordBotLocalSettings()

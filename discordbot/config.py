from pydantic import BaseSettings


class DiscordBotLocalSettings(BaseSettings):

    BOT_TOKEN: str
    TEST_TOKEN: str = None
    TEST: bool = False
    MIX_CHANNEL: int = 927203296685477888
    MARKOV_ALLOWED_CHANNELS: list[int] = [178976406288465920, 469130152882733061]

    class Config:
        env_prefix = 'DISCORD_'
        env_file = '.env'


settings = DiscordBotLocalSettings()

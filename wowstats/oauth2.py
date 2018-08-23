from requests_oauth2 import OAuth2
from VertigoProject.settings import WOW_KEY, WOW_SECRET


class BlizzardAPI(OAuth2):
    """OAuth2 Class for Blizzard API"""
    client_id = WOW_KEY
    client_secret = WOW_SECRET
    site = 'https://eu.battle.net'
    template = 'https://{}.battle.net'
    redirect_uri = 'https://www.epicvertigo.xyz/wow/callback'

import aiohttp
from django.core.exceptions import ImproperlyConfigured
from django.db.models import ImageField
from pydantic import AnyHttpUrl

from discordbot.config import settings
from discordbot.imgur.schemas import ImgurTokenPair


class ImgurClient:
    token_data: ImgurTokenPair = None

    def __init__(self):
        self._session: aiohttp.ClientSession = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if not self._session:
            self._session = aiohttp.ClientSession(
                base_url='https://api.imgur.com',
                timeout=aiohttp.ClientTimeout(total=45)
            )
        return self._session

    async def get_tokens_async(self) -> ImgurTokenPair:
        from discordbot.models import DiscordSettings
        session = await self._get_session()

        try:
            _token = await DiscordSettings.get(settings.IMGUR_REFRESH_TOKEN_DB_KEY)
        except KeyError as exc:
            raise ImproperlyConfigured('Initial refresh token is missing') from exc

        payload = {
            'refresh_token': _token,
            'client_id': settings.IMGUR_CLIENT_ID,
            'client_secret': settings.IMGUR_CLIENT_SECRET,
            'grant_type': 'refresh_token'
        }

        async with session.post('/oauth2/token', data=payload) as response:
            data = await response.json()
            token_data = ImgurTokenPair.validate(data)
            await token_data.save()
            self.token_data = token_data

    async def upload_image(self, obj: ImageField) -> AnyHttpUrl | None:
        if not self.token_data or not self.token_data.is_valid:
            await self.get_tokens_async()

        payload = {'album': settings.IMGUR_ALBUM_HASH, 'image': obj.read()}
        headers = {'Authorization': f'Bearer {self.token_data.access_token}'}
        session = await self._get_session()

        async with session.post('/3/image', headers=headers, data=payload) as response:
            if not response.ok:
                error_data = await response.json()
                raise Exception(error_data.get('data', 'Unknown error'))
            response_data = await response.json()
            return response_data.get('data', {}).get('link')


imgur_client = ImgurClient()

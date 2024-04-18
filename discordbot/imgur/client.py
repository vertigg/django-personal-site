import logging
from json import JSONDecodeError

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from httpx import Client, HTTPError, Response, codes
from pydantic import AnyHttpUrl, BaseModel

from discordbot.config import settings
from discordbot.models import DiscordSettings

logger = logging.getLogger('discord.imgur.client')


class ImgurTokenPair(BaseModel):
    refresh_token: str
    access_token: str


class ImgurClient:
    http_client: Client = None
    _refresh_token = None

    def __init__(self) -> None:
        self.http_client = Client(base_url="https://api.imgur.com", timeout=45)

    @property
    def refresh_token(self) -> str:
        if not self._refresh_token:
            try:
                token = DiscordSettings.get(settings.IMGUR_REFRESH_TOKEN_DB_KEY)
                self._refresh_token = token
            except KeyError as exc:
                raise ImproperlyConfigured("Refresh token must be present in Discord Settings") from exc
        return self._refresh_token

    @property
    def access_token(self) -> str:
        token = cache.get(settings.IMGUR_ACCESS_TOKEN_DB_KEY)
        if not token:
            try:
                db_token = DiscordSettings.get(settings.IMGUR_ACCESS_TOKEN_DB_KEY, None)
                if not db_token:
                    raise ImproperlyConfigured("Database access token is empty")
                cache.set(settings.IMGUR_ACCESS_TOKEN_DB_KEY, db_token)
            except (ImproperlyConfigured, KeyError):
                return self.refresh()
        return token

    def refresh(self):
        # TODO: Works like ass when accessed from multiple celery tasks
        logger.info("Initiate access token refresh for imgur client")
        payload = {
            'refresh_token': self.refresh_token,
            'client_id': settings.IMGUR_CLIENT_ID,
            'client_secret': settings.IMGUR_CLIENT_SECRET,
            'grant_type': 'refresh_token'
        }

        response = self.http_client.post('/oauth2/token', data=payload)

        if response.is_error:
            raise HTTPError("Can't obtain access token")

        data = response.json()
        token_data = ImgurTokenPair.validate(data)

        if not token_data.access_token:
            raise Exception("Error getting new access token")

        DiscordSettings.set(settings.IMGUR_ACCESS_TOKEN_DB_KEY, token_data.access_token)
        cache.set(settings.IMGUR_ACCESS_TOKEN_DB_KEY, token_data.access_token)

    def upload_image(self, image: bytes) -> tuple[AnyHttpUrl, Exception]:
        payload = {'album': settings.IMGUR_ALBUM_HASH}
        files = {'image': image}
        try:
            data = self._make_request("POST", "/3/image", data=payload, files=files)
            link = data.get('link')
            if not link:
                raise Exception("Can't get Image URL after upload")
            return link, None
        except Exception as exc:
            return None, exc

    def _make_headers(self) -> dict[str, str]:
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

    def _make_request(self, method: str, url: str, data: dict = None, files: dict = None):
        headers = self._make_headers()
        response: Response = self.http_client.request(
            method, url, headers=headers, data=data, files=files
        )

        if response.status_code == codes.FORBIDDEN:
            self.refresh()
            headers = self._make_headers()
            response: Response = self.http_client.request(
                method, url, headers=headers, data=data, files=files
            )

        if response.status_code == codes.TOO_MANY_REQUESTS:
            raise HTTPError("Rate-limit exceeded!")

        try:
            json_response = response.json()
        except JSONDecodeError as exc:
            raise HTTPError("JSON decoding failed") from exc

        if 'error' in json_response.get('data', {}):
            raise HTTPError(data.get('data').get('error'))

        return json_response.get('data') or json_response


imgur_client = ImgurClient()

import logging

from httpx import (
    AsyncClient, AsyncHTTPTransport, Client, HTTPTransport, Response
)

logger = logging.getLogger('discord.cogs.utils.http')

DEFAULT_HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1')
}


def httpx_request(
        method: str,
        url: str,
        headers: dict = None,
        data: dict = None,
        retries: int = 5
) -> tuple[Response, Exception]:
    """Generic synchronous httpx request"""
    try:
        with Client(transport=HTTPTransport(retries=retries)) as client:
            response = client.request(
                method=method,
                url=url,
                headers=headers or DEFAULT_HEADERS,
                timeout=30,
                data=data,
                follow_redirects=False,
            )
            return response, None
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.error(exc)
        return None, exc


async def async_httpx_request(
        method: str,
        url: str,
        headers: dict = None,
        data: dict = None,
        retries: int = 5
) -> tuple[Response, Exception]:
    """Generic asynchronous httpx request"""
    try:
        async with AsyncClient(transport=AsyncHTTPTransport(retries=retries)) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers or DEFAULT_HEADERS,
                timeout=30,
                data=data,
                follow_redirects=False,
            )
            return response, None
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.error(exc)
        return None, exc

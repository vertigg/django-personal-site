import asyncio
import logging
from os import path

import magic
from celery import group
from celery.result import AsyncResult
from django.core.files.base import ContentFile
from django.utils.timezone import now

from config.celery import app
from discordbot.cogs.utils.checks import is_allowed_image_mimetype
from discordbot.cogs.utils.http import httpx_request
from discordbot.config import settings
from discordbot.models import MixImage
from discordbot.schemas import ProcessedMixImage

logger = logging.getLogger('discord.imgur.tasks')


@app.task
def process_mix_url(url: str, author_id: int):
    from discordbot.imgur.client import imgur_client

    obj = ProcessedMixImage(url=url, valid=False, filename=path.basename(url.split('?')[0]))

    response, error = httpx_request("HEAD", url, retries=1)
    if error or response.is_error:
        obj.valid = False
        obj.add_error_message("Can't open provided URL")
        return obj.json()

    content_type = response.headers.get('content-type', 'unknown')
    is_valid_type = is_allowed_image_mimetype(content_type)
    if not is_valid_type:
        obj.add_error_message(f"Wrong or unsupported filetype ({content_type})")

    content_length = int(response.headers.get("content-length", settings.MIX_IMAGE_SIZE_LIMIT))
    is_valid_size = content_length < settings.MIX_IMAGE_SIZE_LIMIT
    if not is_valid_size:
        obj.append(f"File is too big (over {settings.MIX_IMAGE_SIZE_LIMIT_MB} MB)")

    if not all((is_valid_type, is_valid_size)):
        obj.valid = False
        return obj.json()

    response, error = httpx_request("GET", url, retries=1)
    if error or response.is_error:
        obj.valid = False
        obj.add_error_message("Can't download file")
        return obj.json()

    if not is_allowed_image_mimetype(magic.from_buffer(response.content, mime=True)):
        obj.valid = False
        obj.add_error_message("Content-Type and filetype mismatch")
        return obj.json()

    content = ContentFile(response.content)

    if MixImage.is_image_exist(content):
        obj.add_error_message("Image already exists in database")
        obj.valid = False
        return obj.json()

    new_db_entry = MixImage(date=now(), author_id=author_id)
    new_db_entry.image.save(obj.filename, content, save=True)

    # Imgur upload
    imgur_url, error = imgur_client.upload_image(content)
    if error:
        obj.add_error_message("Imgur upload failed")
        obj.valid = False
        new_db_entry.delete()
        return obj.json()

    new_db_entry.url = imgur_url
    new_db_entry.save(update_fields=['url'])
    obj.valid = True

    logging.warning(imgur_client.access_token)

    return obj.json()


@app.task
def periodic_access_token_refresh():
    from discordbot.imgur.client import imgur_client
    imgur_client.refresh()


async def wait_result_ready(result: AsyncResult):
    delay = 0.1
    while not result.ready():
        await asyncio.sleep(delay)
        delay = min(delay * 1.5, 2)


async def process_mix_urls_async(urls: list[str], author_id: int) -> tuple[list[ProcessedMixImage], Exception]:
    result = group([process_mix_url.s(url, author_id) for url in urls]).apply_async()
    try:
        await asyncio.wait_for(wait_result_ready(result), timeout=60)
        return [ProcessedMixImage.parse_raw(x) for x in result.get()], None
    except asyncio.TimeoutError as exc:
        return [], exc

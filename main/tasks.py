import hashlib
import logging
import random
import re
from datetime import datetime, timedelta
from functools import cached_property

import requests
from bs4 import BeautifulSoup as Soup
from bs4 import Tag
from celery import Task
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import cache
from httpx import Client

from config.celery import register_task

logger = logging.getLogger("main.tasks")


@register_task
class GenerateBlacklistTask(Task):
    """Generates blacklist IP for Rion"""

    padding = 40
    separator = "#" * padding
    pattern = re.compile(
        r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}(?:\/[0-9]{1,2})?"
    )
    filepath = staticfiles_storage.path("blacklist.txt")
    urls = [
        "https://www.spamhaus.org/drop/drop.txt",
        "https://www.spamhaus.org/drop/edrop.txt",
        "https://sslbl.abuse.ch/blacklist/sslipblacklist.txt",
    ]

    def _center_text(self, text: str) -> str:
        return f"#{text.center(self.padding - 2, ' ')}#"

    @property
    def random_title(self) -> str:
        return random.choice(["PepeLaugh", "WeirdChamp", "monkaShake"])

    def generate_header(self) -> str:
        return "\n".join(
            map(
                self._center_text,
                [
                    f"{self.random_title} IP list",
                    f"Fetched {datetime.now()}",
                    f"Next {datetime.now() + timedelta(days=1)}",
                ],
            )
        )

    def run(self, *args, **options):
        ip_list = []
        for url in self.urls:
            try:
                response = requests.get(url, timeout=30)
                if not response.ok:
                    raise Exception(
                        f"Response returned with status {response.status_code}"
                    )
                ip_list.extend(self.pattern.findall(response.text))
            except Exception as exc:
                logger.error(
                    "Could not fetch IP data from %s. Error details: %s", url, exc
                )
        ip_list = sorted(set(ip_list))
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.writelines(
                "\n".join([self.separator, self.generate_header(), self.separator])
            )
            f.writelines([f"\n{address}" for address in ip_list])


@register_task
class HTTPMonitorTask(Task):
    PREFIX = "web_monitor_task"

    def __init__(self):
        self._client = Client(headers=settings.DEFAULT_HEADERS, timeout=30)
        super().__init__()

    @cached_property
    def tag_sentinel(self) -> Tag:
        t = Tag(name="span", attrs={})
        t.string = "Missing element"
        return t

    def make_result_key(self, url: str) -> str:
        hsh = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return f"{self.PREFIX}_{hsh}"

    def send_telegram_message(self, url: str, current: str, prev: str):
        telegram_url = (
            f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
        )
        response = self._client.post(
            telegram_url,
            data={
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": f"Change detected on {url}.\nFrom {prev} to {current}",
            },
        )
        response.raise_for_status()

    def run(
        self, url: str, selector: str, allow_missing_tags: bool = False, *args, **kwargs
    ):
        logging.info("Starting %s task", self.__name__)

        resp = self._client.get(url)
        resp.raise_for_status()

        soup = Soup(resp.text, features="html.parser")
        element = soup.select_one(selector)

        if not element:
            if allow_missing_tags:
                element = self.tag_sentinel
            else:
                logger.error("%s element wasn't found on %s", selector, url)
                return

        key = self.make_result_key(url)
        value = element.get_text(strip=True)
        cached = cache.get(key, url)

        if cached is None:
            logger.debug("First visit for %s", url)
            cache.set(key, value, timeout=None)
        elif cached != value:
            logger.info("Change detected on %s, notifying", url)
            self.send_telegram_message(url, value, cached)
            cache.set(key, value, timeout=None)
        else:
            logger.debug("No change detected")

import random
import re
from datetime import datetime

import requests
from django.contrib.staticfiles.storage import staticfiles_storage

from main.management.commands.utils import AdvancedCommand


class Command(AdvancedCommand):
    help = 'Generates blacklist IP for Rion'
    padding = 40
    separator = '#' * padding
    pattern = re.compile(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')
    filepath = staticfiles_storage.path('blacklist.txt')
    urls = [
        'https://www.spamhaus.org/drop/drop.txt',
        'https://www.spamhaus.org/drop/edrop.txt',
        'http://osint.bambenekconsulting.com/feeds/c2-ipmasterlist-high.txt',
        'https://sslbl.abuse.ch/blacklist/sslipblacklist.txt',
    ]

    def _center_text(self, text: str) -> str:
        return f'#{text.center(self.padding - 2, " ")}#'

    @property
    def random_title(self) -> str:
        return random.choice(['OMEGALUL', 'WeirdChamp', 'OkayChamp'])

    def generate_header(self) -> str:
        return '\n'.join(map(self._center_text, [
            f'{self.random_title} IP list',
            f'Fetched {datetime.now()}',
            f'Generated in {self.execution_time} seconds'
        ]))

    def handle(self, *args, **options):
        ip_list = []

        for url in self.urls:
            try:
                response = requests.get(url)
                ip_list.extend(self.pattern.findall(response.text))
            except Exception as exc:
                self.logger.error(f'Could not fetch IP data from {url}. '
                                  f'Error details: {str(exc)}')

        ip_list = sorted(set(ip_list))

        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.writelines('\n'.join([self.separator, self.generate_header(), self.separator]))
            f.writelines([f'\n{x}/24' for x in ip_list])
        self.log_execution_time()

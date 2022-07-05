import random
import re
from datetime import datetime, timedelta

import requests
from django.contrib.staticfiles.storage import staticfiles_storage
from main.management.commands.utils import AdvancedCommand


class Command(AdvancedCommand):
    help = 'Generates blacklist IP for Rion'
    padding = 40
    separator = '#' * padding
    pattern = re.compile(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}(?:\/[0-9]{1,2})?')
    filepath = staticfiles_storage.path('blacklist.txt')
    urls = [
        'https://www.spamhaus.org/drop/drop.txt',
        'https://www.spamhaus.org/drop/edrop.txt',
        'https://sslbl.abuse.ch/blacklist/sslipblacklist.txt',
    ]

    def _center_text(self, text: str) -> str:
        return f'#{text.center(self.padding - 2, " ")}#'

    @property
    def random_title(self) -> str:
        return random.choice(['PepeLaugh', 'WeirdChamp', 'monkaShake'])

    def generate_header(self) -> str:
        return '\n'.join(map(self._center_text, [
            f'{self.random_title} IP list',
            f'Fetched {datetime.now()}',
            f'Next {datetime.now() + timedelta(days=1)}',
            f'Generated in {self.execution_time} second(s)',
        ]))

    def handle(self, *args, **options):
        ip_list = []
        for url in self.urls:
            try:
                response = requests.get(url, timeout=30)
                if not response.ok:
                    raise Exception(f'Response returned with status {response.status_code}')
                ip_list.extend(self.pattern.findall(response.text))
            except Exception as exc:
                self.logger.error(
                    'Could not fetch IP data from %s. Error details: %s', url, exc
                )
        ip_list = sorted(set(ip_list))
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.writelines('\n'.join([self.separator, self.generate_header(), self.separator]))
            f.writelines([f'\n{address}' for address in ip_list])
        self.log_execution_time()

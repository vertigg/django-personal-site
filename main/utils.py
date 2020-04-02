import re
from datetime import datetime
from io import StringIO

import requests
from django.contrib.staticfiles.storage import staticfiles_storage

BLACKLIST_FILEPATH = staticfiles_storage.path('blacklist.txt')
BLACKLIST_URL = staticfiles_storage.url('blacklist.txt')


def generate_blacklist():
    pattern = re.compile(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')
    urls = [
        'https://www.spamhaus.org/drop/drop.txt',
        'https://www.spamhaus.org/drop/edrop.txt',
        'http://osint.bambenekconsulting.com/feeds/c2-ipmasterlist-high.txt',
        'https://sslbl.abuse.ch/blacklist/sslipblacklist.txt',
    ]
    ip_list = []
    for url in urls:
        response = requests.get(url)
        ip_list.extend(pattern.findall(response.text))
    ip_list = sorted(set(ip_list))

    with open(BLACKLIST_FILEPATH, 'w', encoding='utf-8') as f:
        f.write(
            f'{"#"*40}\n# Omegalul IP list\n# Fetched {datetime.now()}\n{"#"*40}\n')
        f.writelines([f'{x}/24\n' for x in ip_list])

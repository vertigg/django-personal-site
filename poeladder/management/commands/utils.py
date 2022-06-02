import logging
import time
from itertools import groupby, zip_longest

import requests
from poeladder.models import PoeActiveGem
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.getLogger(__name__)


def requests_retry_session(
        retries=5,
        backoff_factor=1.2,
        status_forcelist=(429, 500, 502, 504, 522),
        session=None):
    """Create a requests Session object pre-configured for retries

    Args:
        retries (int): number of times to retry request
        backoff_factor (float): amount of time to wait between retries
        status_forcelist (list): http status codes to ignore during retries
        session (Session): optional Session object to apply retry config to

    Returns:
        Session: requests Session object configured for retries

    """
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )

    session = session or requests.Session()
    adapter = HTTPAdapter(max_retries=retry)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update({
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
        )
    })

    return session


def detect_skills(request_data):
    """Detect 5 or 6 links with active skills in character data"""
    # TODO: Detect "built-in" item gems (like flame burst for example)
    gems_ids, active_gems = list(), list()

    for item in request_data.get('items', []):
        # Ignore items in main inventory and secondary weapon (TODO: allow secondary weapon)
        if item.get('inventoryId') in {'MainInventory'}:
            continue

        # Item must have at least 5 or 6 sockets
        sockets = item.get('sockets', [])
        if not sockets or len(sockets) < 5:
            continue

        # zip sockets and socketed items if possible
        socketed_items = {x.get('socket'): x for x in item.get('socketedItems')}
        gems = list()
        for index, socket in enumerate(sockets):
            gem = socketed_items.get(index, {})
            gems.append({
                'group_id': socket.get('group'),
                'name': gem.get('typeLine'),
                'icon': gem.get('icon'),
                'support': gem.get('support')
            })

        # Group gems by links
        for _, group in groupby(gems, lambda x: x.get('group_id')):
            link_group = list(group)
            if len(link_group) >= 5:
                # If some sockets are empty - skip processing
                if not all([x.get('name') for x in link_group]):
                    continue
                # At least 2 support gems must be present in link
                if len([x for x in link_group if x.get('support')]) < 2:
                    continue
                # Add all active gems to character
                active_gems.extend([
                    {x['name']: x['icon']} for x
                    in link_group if not x.get('support')
                ])

    time.sleep(1)

    # Check if there are less than 3 active skills in link
    if 0 < len(active_gems) <= 3:
        cached_gems_qs = PoeActiveGem.objects.values_list('name', 'id')
        cached_gems = {x[0]: x[1] for x in cached_gems_qs}

        # Check if skills exists in db
        for gem in active_gems:
            for name, icon in gem.items():
                if name in cached_gems:
                    gems_ids.append(cached_gems[name])
                else:
                    new_gem = PoeActiveGem.objects.create(
                        name=name, icon=icon)  # check if create() is faster
                    gems_ids.append(new_gem.id)
    return gems_ids

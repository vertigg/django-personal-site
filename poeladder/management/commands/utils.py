import logging
import time
from itertools import groupby

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from poeladder.models import PoeActiveGem

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

    gems_ids = []
    active_gems = []

    # Check if character has items
    if request_data.get('items'):
        for item in request_data['items']:

            # Check if item has sockets
            item_sockets = item.get('sockets', None)

            # If item has sockets and it's not in main inventory
            # or in Slot Weapon 2 (Thanks Inked)
            if item_sockets and item['inventoryId'] != 'MainInventory' and item['inventoryId'] != 'Weapon2':
                groups_temp = []

                # Get socket groups
                for socket in item_sockets:
                    groups_temp.append(socket['group'])

                # Check if group has 5 or 6 linked sockets
                socket_groups = [len(list(group))
                                 for key, group in groupby(groups_temp)]
                for socket_group in socket_groups:
                    if socket_group >= 5:

                        # Get ids for linked sockets
                        linked_sockets = []
                        for i in range(len(item_sockets)):
                            if item_sockets[i]['group'] == socket_groups.index(socket_group):
                                linked_sockets.append(i)

                        # Check if sockets not empty
                        if not len(linked_sockets) > len(item['socketedItems']):

                            # Check linked sockets for active gems
                            for linked_socket in linked_sockets:
                                for socketed_item in item['socketedItems']:
                                    if socketed_item['socket'] == linked_socket and not socketed_item['support']:
                                        active_gems.append(
                                            {socketed_item['typeLine']: socketed_item['icon']})
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

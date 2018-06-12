import logging
import time
from functools import wraps
from itertools import groupby

from django.db.utils import OperationalError
from poeladder.models import PoeActiveGem

logging.getLogger(__name__)

def retry_on_lock(timeout=None, retries=1):
    if not timeout:
        timeout = 5
    def outer_decorator(func):
        @wraps(func)
        def inner_decorator(*args, **kwargs):
            nonlocal retries
            while retries >= 1:
                try:
                    func(*args, **kwargs)
                    break
                except OperationalError as e:
                    logging.error('{0}. Waiting for {1} seconds. Retries left: {2}'.format(repr(e), timeout, retries))
                    time.sleep(timeout)
                    retries -= 1
                except Exception as e:
                    logging.error(repr(e))
                    quit()

            if retries <= 0:
                logging.error("Can't connect to db")
                quit()

        return inner_decorator
    return outer_decorator


def detect_skills(request_data):
    """Detect 5 or 6 links with active skills in character data"""

    gems_ids = []
    active_gems = []

    # Check if character has items
    if request_data.get('items'):
        for item in request_data['items']:

            # Check if item has sockets
            item_sockets = item.get('sockets', None)

            # If item has sockets and it's not in main inventory or in Slot Weapon 2 (Thanks Inked)
            if item_sockets and item['inventoryId'] != 'MainInventory' and item['inventoryId'] != 'Weapon2':
                groups_temp = []

                # Get socket groups
                for socket in item_sockets:
                    groups_temp.append(socket['group'])

                # Check if group has 5 or 6 linked sockets
                socket_groups = [len(list(group)) for key, group in groupby(groups_temp)]
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
                                        active_gems.append({socketed_item['typeLine'] : socketed_item['icon']})
        time.sleep(1)

        # Check if there are less than 3 active skills in link
        if len(active_gems) <= 3 and len(active_gems) > 0:
            cached_gems_qs = PoeActiveGem.objects.values_list('name', 'id')
            cached_gems = {x[0] : x[1] for x in cached_gems_qs}

            # Check if skills exists in db
            for gem in active_gems:
                for name, icon in gem.items():
                    if name in cached_gems:
                        gems_ids.append(cached_gems[name])
                    else:
                        new_gem = PoeActiveGem.objects.create(name=name, icon=icon) # check if create() is faster
                        gems_ids.append(new_gem.id)
    return gems_ids

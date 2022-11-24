import time
from itertools import groupby

from poe.models import ActiveGem


def detect_skills(request_data):
    """Detect 5 or 6 links with active skills in character data"""
    # TODO: Detect "built-in" item gems (like flame burst for example)
    gems_ids, active_gems = list(), list()

    for item in request_data.get('items', []):
        # Ignore items in main inventory and secondary weapon
        if item.get('inventoryId') == 'MainInventory':
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

    # Check if there are less than 4 active skills in link
    if 0 < len(active_gems) <= 4:
        cached_gems_qs = ActiveGem.objects.values_list('name', 'id')
        cached_gems = {x[0]: x[1] for x in cached_gems_qs}

        # Check if skills exists in db
        for gem in active_gems:
            for name, icon in gem.items():
                if name in cached_gems:
                    gems_ids.append(cached_gems[name])
                else:
                    new_gem = ActiveGem.objects.create(
                        name=name, icon=icon)  # check if create() is faster
                    gems_ids.append(new_gem.id)
    return gems_ids

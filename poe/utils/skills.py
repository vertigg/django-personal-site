import re
import time
from collections import defaultdict

from poe.models import ActiveGem

BUILT_IN_SUPPORT_PATTERN = re.compile(r'Supported by (?P<level>Level \d{1,2}) (?P<name>\w+)')
ALLOWED_ITEM_TYPES = {'Weapon', 'Weapon2', 'Offhand', 'Offhand2', 'BodyArmour', 'Boots', 'Gloves', 'Helm'}
IGNORE_ACTIVE_GEMS = frozenset([
    'War Banner',
    'Vitality',
    'Flesh and Stone',
    'Defiance Banner',
    'Determination',
    'Anger',
    'Purity of Fire',
    'Dread Banner',
    'Pride',
    'Precision',
    'Haste',
    'Grace',
    'Hatred',
    'Purity of Ice',
    'Clarity',
    'Summon Skitterbots',
    'Purity of Elements',
    'Discipline',
    'Wrath',
    'Purity of Lightning',
    'Zealotry',
    'Malevolence',
    'Portal',
    'Detonate Mines',
    'Vaal Grace',
    'Vaal Haste',
    'Vaal Impurity of Ice',
    'Vaal Impurity of Lightning',
    'Vaal Impurity of Fire',
    'Vaal Discipline',
    'Vaal Breach'
])


def detect_skills(request_data):
    """Detect 5 or 6 links with active skills in character data"""
    # TODO: Detect "built-in" item gems (like flame burst for example)
    gems_ids, active_gems = [], []

    for item in request_data.get('items', []):
        if item.get('inventoryId') not in ALLOWED_ITEM_TYPES:
            continue

        # Item must have at least 5 or 6 sockets
        sockets = item.get('sockets', [])
        if not sockets:  # or len(sockets) < 5:
            continue

        # zip sockets and socketed items if possible
        socketed_items = {x.get('socket'): x for x in item.get('socketedItems')}
        groups = defaultdict(list)
        for index, socket in enumerate(sockets):
            if gem := socketed_items.get(index):
                if gem.get('typeLine') not in IGNORE_ACTIVE_GEMS:
                    groups[socket.get('group')].append({
                        'name': gem.get('typeLine'),
                        'icon': gem.get('icon'),
                        'support': gem.get('support'),
                    })

        # Check for "built-in" support gems and add it to any available group
        for mod in item.get('explicitMods', []):
            if match := BUILT_IN_SUPPORT_PATTERN.search(mod):
                for id, group in groups.items():
                    group.append({
                        'name': match.groupdict().get('name', 'Implicit support'),
                        'icon': None,
                        'support': True
                    })

        # Group gems by links
        # for _, group in groupby(gems, lambda x: x.get('group_id')):
        for group in groups.values():
            if len(group) >= 5:
                # At least 2 support gems must be present in link
                if len([x for x in group if x.get('support')]) < 2:
                    continue
                # Add all active gems to character
                active_gems.extend([
                    {x['name']: x['icon']} for x
                    in group if not x.get('support')
                ])

    time.sleep(1)  # ???

    # Check if there are less than 4 active skills in link
    if 0 < len(active_gems) <= 4:
        cached_gems = dict(ActiveGem.objects.values_list('name', 'id'))

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

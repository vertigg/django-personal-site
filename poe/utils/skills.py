import time
from collections import defaultdict

from poe.models import ActiveGem
from poe.schema import SocketedGemSchema

ALLOWED_ITEM_TYPES = {
    'Weapon', 'Weapon2', 'Offhand', 'Offhand2', 'BodyArmour',
    'Boots', 'Gloves', 'Helm'
}

INVALID_ACTIVE_GEMS = frozenset([
    'War Banner', 'Vitality', 'Flesh and Stone', 'Defiance Banner', 'Anger',
    'Determination', 'Purity of Fire', 'Dread Banner', 'Pride', 'Precision',
    'Haste', 'Grace', 'Hatred', 'Purity of Ice', 'Clarity', 'Discipline',
    'Summon Skitterbots', 'Purity of Elements', 'Wrath', 'Purity of Lightning',
    'Zealotry', 'Malevolence', 'Portal', 'Detonate Mines', 'Vaal Grace',
    'Vaal Haste', 'Vaal Impurity of Ice', 'Vaal Impurity of Lightning',
    'Vaal Impurity of Fire', 'Vaal Discipline', 'Vaal Breach'
])


def detect_active_skills(request_data) -> list[int]:
    """Detect 5 or 6 links with active skills in character data"""
    active_gems: list[SocketedGemSchema] = []
    gem_ids: int = []

    for item in request_data.get('items', []):
        if item.get('inventoryId') not in ALLOWED_ITEM_TYPES:
            continue

        # Item must have any sockets with something socketed in it
        sockets = item.get('sockets', [])
        socketed_items = item.get('socketedItems', [])

        if not sockets or not socketed_items:
            continue

        # Build linked gem groups based on sockets and items
        groups: dict[int, list[SocketedGemSchema]] = defaultdict(list)

        for gem_data in socketed_items:
            group_id = sockets[gem_data.get('socket')].get('group')
            gem = SocketedGemSchema(**gem_data)
            if gem.is_support or gem.name not in INVALID_ACTIVE_GEMS:
                groups[group_id].append(gem)

        # Check for "built-in" support gems and add it to all available groups
        for mod in item.get('explicitMods', []):
            if 'supported by level' in mod.lower():
                for group in groups.values():
                    group.append(SocketedGemSchema(typeLine='Built-In support', support=True))

        # Validate and detect active gems in 5-6 links
        for group in groups.values():
            if len(group) >= 5:
                # At least 2 support gems must be present in link
                if len([gem for gem in group if gem.is_support]) < 2:
                    continue
                # Add all active gems to character
                active_gems.extend([gem for gem in group if gem.is_active])

    time.sleep(1)

    # Check if there are less than 4 active skills in link
    if 0 < len(active_gems) <= 4:
        cached_gems = dict(ActiveGem.objects.values_list('name', 'id'))
        # Check if skills exists in db
        for gem in active_gems:
            # for name, icon in gem.items():
            if gem.name in cached_gems:
                gem_ids.append(cached_gems[gem.name])
            else:
                new_gem = ActiveGem.objects.create(name=gem.name, icon=gem.icon)
                gem_ids.append(new_gem.id)
    return gem_ids

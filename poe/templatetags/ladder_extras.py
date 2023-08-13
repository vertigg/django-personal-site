from django import template
from poe.utils.experience_table import EXPERIENCE_TABLE

register = template.Library()


def calculate_progress(level: int, current_experience: int) -> float:
    diff = EXPERIENCE_TABLE[level + 1]['total_xp'] - current_experience
    return round((1 - (diff / EXPERIENCE_TABLE[level]['xp_to_gain'])) * 100, 2)


@register.filter
def level_progress(character):
    if character.level == 100:
        return character.level
    if character.experience:
        return calculate_progress(character.level, character.experience)


@register.filter
def space_separator(number: int) -> str:
    return f'{number:,}'.replace(',', ' ')


@register.filter
def float_compact_format(num: int):
    if not num:
        return None
    round_to = 1
    magnitude = 0
    abbr = ['', 'K', 'M', 'B', 'T', 'Q']
    while abs(num) >= 1000:
        magnitude += 1
        num = round(num / 1000.0, round_to)
    return f'{num:.{round_to}f}{abbr[magnitude]}'

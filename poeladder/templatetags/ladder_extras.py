from django import template
from poeladder.utils.experience_table import experience

register = template.Library()


def calculate_progress(level, current_experience):
    diff = experience[level + 1]['total_xp'] - current_experience
    return round((1 - (diff / experience[level]['xp_to_gain'])) * 10, 2)


@register.filter
def level_progress(character):
    if character.level == 100:
        return 100
    if character.experience:
        return calculate_progress(character.level, character.experience)


@register.filter
def space_separator(exp):
    return "{:,}".format(exp).replace(',', ' ')

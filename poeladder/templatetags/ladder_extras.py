from django import template
from poeladder.utils.experience_table import experience

register = template.Library()


@register.filter
def level_progress(character):
    if character.level == 100:
        return 100
    if character.experience:
        diff = experience[character.level +
                          1]['total_xp'] - character.experience
        exp_percentage = round(
            (1 - (diff / experience[character.level]['xp_to_gain'])) * 100, 2)
        return exp_percentage


@register.filter
def space_separator(exp):
    return "{:,}".format(exp).replace(',', ' ')

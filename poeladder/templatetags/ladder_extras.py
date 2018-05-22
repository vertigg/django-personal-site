from django import template
from poeladder.experience_table import experience

register = template.Library()

@register.filter
def to_dash(text):
    return text.replace(' ','-')

@register.filter
def level_progress(character):
    if character.level == 100:
        return 100
    exp_difference = experience[character.level+1]['total_xp'] - character.experience
    exp_percentage = round(1 - (exp_difference/experience[character.level]['xp_to_gain']), 2) * 100
    return exp_percentage
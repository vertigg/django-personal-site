from django import template

register = template.Library()

@register.filter
def webp(value):
    """Replaces webp with jpg (For firefox)"""
    return value.replace("webp","jpg")
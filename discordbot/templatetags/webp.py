from django import template

register = template.Library()


@register.filter
def discord_avatar_to_jpg(value):
    """Replaces webp extension with jpg (For Discord avatars)"""
    return value.replace("webp", "jpg")

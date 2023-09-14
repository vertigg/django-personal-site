from django import template

register = template.Library()


@register.filter
def discord_avatar_to_jpg(url: str) -> str:
    """Replaces webp extension in url with jpg (For Discord avatars)"""
    return url.replace("webp", "jpg") if url.endswith('.jpg') else url

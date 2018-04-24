from django import template

register = template.Library()

@register.filter
def webp(value):
    return value.replace("webp","jpg")
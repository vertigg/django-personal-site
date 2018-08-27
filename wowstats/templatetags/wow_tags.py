from django import template

register = template.Library()


@register.simple_tag
def show_difference(latest, previous):
    if previous:
        diff = int(latest) - int(previous)
        if diff > 0:
            return "{0} ({1})".format(latest, str(diff))
        else:
            return "{0} ({1})".format(latest, str(diff))
    else:
        return latest

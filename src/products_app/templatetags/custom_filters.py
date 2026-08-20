from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Sépare une chaîne par un délimiteur"""
    if not value:
        return []
    return value.split(arg)


@register.filter
def trim(value):
    """Supprime les espaces en début et fin de chaîne"""
    if not value:
        return ''
    return value.strip()
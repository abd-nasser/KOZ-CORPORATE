from django import template
from datetime import datetime

register = template.Library()

@register.filter
def iso_to_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
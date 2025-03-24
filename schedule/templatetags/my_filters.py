# my_filters.py

from django import template

register = template.Library()

@register.filter
def get_range(value):
    return range(value)

@register.filter
def get_item(value, key):
    if isinstance(value, dict):
        return value.get(key, None)
    else:
        return None  # もしくは適切な処理を行う
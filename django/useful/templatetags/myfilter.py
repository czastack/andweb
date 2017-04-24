from django import template

register = template.Library()

@register.filter
def getitem(obj, key):
    value = getattr(obj, key, None)
    if value is None and hasattr(obj, 'get'):
        value = obj.get(key, None)
    return value
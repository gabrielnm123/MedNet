from django import template
import re

register = template.Library()

@register.filter
def match(value, arg):
    return re.match(arg, value)

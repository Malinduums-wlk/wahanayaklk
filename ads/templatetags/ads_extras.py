from django import template

register = template.Library()

@register.filter
def underscore_space(value):
    """Replace underscores with spaces in a string."""
    if not isinstance(value, str):
        return value
    return value.replace('_', ' ')

@register.filter
def to_wa(value):
    """Convert a local SL phone number starting with 0 or +94 to 94XXXXXXXXX suitable for wa.me links."""
    if not isinstance(value, str):
        return value
    digits = ''.join(filter(str.isdigit, value))
    if digits.startswith('0'):
        return '94' + digits[1:]
    if digits.startswith('94'):
        return digits
    if digits.startswith('0094'):
        return digits[2:]
    return digits 
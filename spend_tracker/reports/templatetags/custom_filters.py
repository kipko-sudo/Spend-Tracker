from django import template

register = template.Library()

@register.filter
def div(value, arg):
    """Divides the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0

@register.filter
def currency(value):
    """Formats a number as currency"""
    try:
        return f"${float(value):.2f}"
    except ValueError:
        return "$0.00"

@register.filter
def percentage(value, decimals=1):
    """Formats a number as a percentage"""
    try:
        return f"{float(value):.{decimals}f}%"
    except ValueError:
        return "0%"
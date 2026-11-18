from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def soles(monto):
    """2199 -> 'S/ 2 199.00'. Miles separados con espacio fino, como en una boleta."""
    entero, dec = f'{Decimal(monto or 0):,.2f}'.split('.')
    return f'S/ {entero.replace(",", "\u202f")}.{dec}'

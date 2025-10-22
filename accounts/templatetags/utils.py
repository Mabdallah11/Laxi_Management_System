from django import template
from ..utils import calculate_outstanding_balance

register = template.Library()

@register.filter
def calculate_outstanding_balance(lease):
    """Template filter to calculate outstanding balance for a lease."""
    return calculate_outstanding_balance(lease)

from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)

@register.filter
def get_inventory_item(dictionary, key):
    """Get inventory item list, return empty list if not found"""
    result = dictionary.get(key, [])
    return result if isinstance(result, list) else []

@register.filter
def get_order_item(dictionary, key):
    """Get order item quantity by composite key, return 0 if not found"""
    return dictionary.get(str(key), 0)

@register.filter
def make_key(product_id, inventory_id):
    """Create composite key for order items"""
    return f"{product_id}_{inventory_id}"

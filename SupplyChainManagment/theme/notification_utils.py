from django.contrib import messages
from django.utils.html import format_html

def send_toast_notification(request, notification_type, title, text, icon="fa-bell"):
    """
    Send a toast notification using Django messages system
    
    Args:
        request: Django request object
        notification_type: Type of notification (order, shipment, product, inventory, invoice, supplier)
        title: Notification title
        text: Notification text
        icon: FontAwesome icon class
    """
    # Create formatted message with icon and styling
    message_html = format_html(
        '<i class="fad {} mr-2"></i><strong>{}</strong><br><small>{}</small>',
        icon, title, text
    )
    
    # Determine message type for styling
    if notification_type == 'order':
        messages.success(request, message_html)
    elif notification_type == 'shipment':
        messages.info(request, message_html)
    elif notification_type == 'product':
        messages.success(request, message_html)
    elif notification_type == 'inventory':
        messages.warning(request, message_html)
    elif notification_type == 'invoice':
        messages.success(request, message_html)
    elif notification_type == 'supplier':
        messages.info(request, message_html)
    else:
        messages.info(request, message_html)

def notify_new_order(request, order):
    """Send notification for new order"""
    send_toast_notification(
        request, 
        'order',
        f'New Order #{order.id}',
        f'Order placed by {order.ordered_by.username}',
        'fa-shopping-cart'
    )

def notify_shipment_dispatched(request, shipment):
    """Send notification for shipment dispatch"""
    send_toast_notification(
        request,
        'shipment', 
        f'Shipment Dispatched',
        f'Order #{shipment.order.id} - Tracking: {shipment.tracking_number}',
        'fa-shipping-fast'
    )

def notify_product_added(request, product):
    """Send notification for new product"""
    send_toast_notification(
        request,
        'product',
        f'New Product Added',
        f'{product.name} has been added to inventory',
        'fa-box'
    )

def notify_low_inventory(request, inventory_item):
    """Send notification for low inventory"""
    send_toast_notification(
        request,
        'inventory',
        f'Low Inventory Alert',
        f'{inventory_item.product.name} - Only {inventory_item.quantity} left in stock',
        'fa-exclamation-triangle'
    )

def notify_invoice_paid(request, invoice):
    """Send notification for paid invoice"""
    send_toast_notification(
        request,
        'invoice',
        f'Invoice Paid',
        f'Invoice #{invoice.invoice_number} for Order #{invoice.order.id}',
        'fa-file-invoice-dollar'
    )

def notify_supplier_registered(request, supplier):
    """Send notification for new supplier"""
    send_toast_notification(
        request,
        'supplier',
        f'New Supplier Registered',
        f'{supplier.name} - Contact: {supplier.contact_person}',
        'fa-user-plus'
    )

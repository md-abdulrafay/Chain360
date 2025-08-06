from django.shortcuts import render, redirect, get_object_or_404
from .models import Order
from .forms import OrderForm
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import OrderItem
from django.contrib import messages
from inventory.models import InventoryItem
from django.utils.timezone import make_aware, is_aware
from theme.notification_utils import notify_new_order

# Create your views here.



@login_required
def add_order(request):
    products = Product.objects.all()
    
    # Group inventory items by product to show all available units
    inventory_by_product = {}
    
    # Initialize empty lists for all products first
    for product in products:
        inventory_by_product[product.id] = []
    
    # Then populate with actual inventory data
    for item in InventoryItem.objects.select_related('product'):
        cost_price = item.cost_price
        selling_price = item.selling_price
        profit_margin = selling_price - cost_price if cost_price and selling_price else 0
        
        inventory_by_product[item.product.id].append({
            'id': item.id,
            'quantity': item.quantity,
            'unit': item.unit,
            'unit_display': item.get_unit_display(),
            'cost_price': cost_price,  # Use inventory's unit-specific cost price
            'selling_price': selling_price,  # Use inventory's unit-specific selling price
            'profit_margin': profit_margin  # Calculate profit for this unit
        })
    
    # Keep old format for backward compatibility (use first inventory item)
    inventory = {}
    inventory_items = {}
    inventory_units = {}
    for item in InventoryItem.objects.all():
        if item.product.id not in inventory:  # Only take first entry per product
            inventory[item.product.id] = item.quantity
            inventory_items[item.product.id] = item
            inventory_units[item.product.id] = item.get_unit_display()
    if request.method == 'POST':
        status = request.POST.get('status', 'pending')
        order_date_str = request.POST.get('order_date')
        customer_name = request.POST.get('customer_name', 'Walk-in Customer')
        customer_email = request.POST.get('customer_email', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        customer_address = request.POST.get('customer_address', '').strip()
        
        import datetime
        if order_date_str:
            dt = datetime.datetime.strptime(order_date_str, '%Y-%m-%d')  # Only date, no time
            if not is_aware(dt):
                order_date = make_aware(dt)
            else:
                order_date = dt
        else:
            from django.utils.timezone import now
            order_date = now().date()  # Only date
        
        order = Order.objects.create(
            customer_name=customer_name,
            customer_email=customer_email if customer_email else None,
            customer_phone=customer_phone if customer_phone else None,
            customer_address=customer_address if customer_address else None,
            status=status,
            ordered_by=request.user,
            quantity=0,  # Will update after adding items
            product=products.first(),  # Dummy, not used for multi-product
            order_date=order_date
        )
        total_quantity = 0
        total_order_value = 0
        total_profit = 0
        
        # Process each inventory item separately
        for product in products:
            for inv_item_data in inventory_by_product.get(product.id, []):
                inv_item_id = inv_item_data['id']
                field_name = f'quantity_{product.id}_{inv_item_id}'
                qty = int(request.POST.get(field_name, 0))
                
                if qty > 0:
                    # Get the actual inventory item
                    try:
                        inv_item = InventoryItem.objects.get(id=inv_item_id)
                        
                        if inv_item.quantity >= qty:
                            # Create OrderItem with unit-specific prices from inventory
                            order_item = OrderItem.objects.create(
                                order=order, 
                                product=product, 
                                quantity=qty,
                                unit_selling_price=inv_item.selling_price,  # Use inventory's unit-specific price
                                unit_cost_price=inv_item.cost_price,  # Use inventory's unit-specific price
                                inventory_item=inv_item  # Link to specific inventory item
                            )
                            
                            total_order_value += order_item.total_price
                            total_profit += order_item.total_profit
                            
                            # Subtract from specific inventory item
                            inv_item.quantity -= qty
                            inv_item.save()
                            
                            total_quantity += qty
                        else:
                            order.delete()
                            messages.error(request, f'Not enough inventory for {product.name} ({inv_item.get_unit_display()}). Available: {inv_item.quantity}')
                            return render(request, 'add_order.html', {
                                'products': products, 
                                'inventory': inventory, 
                                'inventory_items': inventory_items, 
                                'inventory_units': inventory_units,
                                'inventory_by_product': inventory_by_product
                            })
                    except InventoryItem.DoesNotExist:
                        order.delete()
                        messages.error(request, f'Inventory item not found for {product.name}.')
                        return render(request, 'add_order.html', {
                            'products': products, 
                            'inventory': inventory, 
                            'inventory_items': inventory_items, 
                            'inventory_units': inventory_units,
                            'inventory_by_product': inventory_by_product
                        })
        if total_quantity == 0:
            order.delete()
            messages.error(request, 'Please enter quantity for at least one product.')
            return render(request, 'add_order.html', {
                'products': products, 
                'inventory': inventory, 
                'inventory_items': inventory_items, 
                'inventory_units': inventory_units,
                'inventory_by_product': inventory_by_product
            })
        
        order.quantity = total_quantity
        order.save()
        
        # Send real-time toast notification
        notify_new_order(request, order)
        
        # Success message with profit information
        messages.success(request, f'Order placed successfully! Total Value: ${total_order_value:.2f}, Expected Profit: ${total_profit:.2f}')
        request.session['show_success'] = True
        return redirect('order_list')
    return render(request, 'add_order.html', {
        'products': products, 
        'inventory': inventory, 
        'inventory_items': inventory_items, 
        'inventory_units': inventory_units,
        'inventory_by_product': inventory_by_product
    })

@login_required
def order_list(request):
    # All users can see all customer orders (this is for sales, not purchases)
    orders = Order.objects.all().prefetch_related('items')
    
    # Add calculated totals to each order
    orders_with_totals = []
    for order in orders:
        total_value = sum(item.total_price for item in order.items.all())
        total_profit = sum(item.total_profit for item in order.items.all())
        order.calculated_total_value = total_value
        order.calculated_total_profit = total_profit
        orders_with_totals.append(order)
    
    return render(request, 'order_list.html', {'orders': orders_with_totals})

@login_required
def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    products = Product.objects.all()
    
    # Build inventory by product structure (same as add_order)
    inventory_by_product = {}
    for product in products:
        inventory_by_product[product.id] = []
    
    # Populate inventory for each product with different units
    for item in InventoryItem.objects.select_related('product'):
        cost_price = item.cost_price
        selling_price = item.selling_price
        profit_margin = selling_price - cost_price if cost_price and selling_price else 0
        
        inventory_by_product[item.product.id].append({
            'id': item.id,
            'quantity': item.quantity,
            'unit': item.unit,
            'unit_display': item.get_unit_display(),
            'current_order_qty': 0,  # Will be updated below
            'cost_price': cost_price,  # Use inventory's unit-specific cost price
            'selling_price': selling_price,  # Use inventory's unit-specific selling price
            'profit_margin': profit_margin  # Calculate profit for this unit
        })
    
    # Get current order items and update inventory data with current order quantities
    order_items = {}
    for item in order.items.all().select_related('product'):
        if item.inventory_item:
            key = f"{item.product.id}_{item.inventory_item.id}"
            order_items[key] = item.quantity
            
            # Find the corresponding inventory item and add current order quantity
            for inv_data in inventory_by_product.get(item.product.id, []):
                if inv_data['id'] == item.inventory_item.id:
                    inv_data['current_order_qty'] = item.quantity
                    # Add current order quantity to available quantity for max calculation
                    inv_data['quantity'] += item.quantity
                    print(f"Debug: Product {item.product.name}, Inventory {item.inventory_item.id}, Current Order Qty: {item.quantity}, Updated Available: {inv_data['quantity']}")
                    break
        else:
            # Handle legacy orders without inventory_item reference
            key = f"{item.product.id}_legacy"
            order_items[key] = item.quantity
    
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        customer_email = request.POST.get('customer_email', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        customer_address = request.POST.get('customer_address', '').strip()
        status = request.POST.get('status', 'pending')
        
        # Clear existing order items and restore inventory
        for item in order.items.all():
            # Restore inventory if inventory_item exists
            if item.inventory_item:
                item.inventory_item.quantity += item.quantity
                item.inventory_item.save()
            item.delete()
        
        # Process new quantities for each inventory item
        total_quantity = 0
        has_items = False
        
        for product in products:
            for inv_item_data in inventory_by_product.get(product.id, []):
                inv_item_id = inv_item_data['id']
                qty_str = request.POST.get(f'quantity_{product.id}_{inv_item_id}', '0')
                # Handle empty strings and convert to int
                try:
                    qty = int(qty_str) if qty_str.strip() else 0
                except (ValueError, AttributeError):
                    qty = 0
                
                if qty > 0:
                    # Check if enough inventory
                    inv_item = InventoryItem.objects.get(id=inv_item_id)
                    if qty > inv_item.quantity:
                        messages.error(request, f'Not enough inventory for {product.name} ({inv_item.get_unit_display()}). Available: {inv_item.quantity}')
                        # Restore previously cleared items
                        for restored_item in order.items.all():
                            restored_item.inventory_item.quantity -= restored_item.quantity
                            restored_item.inventory_item.save()
                        return render(request, 'edit_order.html', {
                            'order': order,
                            'products': products,
                            'order_items': order_items,
                            'inventory_by_product': inventory_by_product
                        })
                    
                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        inventory_item=inv_item,
                        quantity=qty,
                        unit_selling_price=product.selling_price,
                        unit_cost_price=product.cost_price or 0
                    )
                    
                    # Update inventory
                    inv_item.quantity -= qty
                    inv_item.save()
                    
                    total_quantity += qty
                    has_items = True
        
        if not has_items:
            messages.error(request, 'Please add at least one product to the order.')
            return render(request, 'edit_order.html', {
                'order': order,
                'products': products,
                'order_items': order_items,
                'inventory_by_product': inventory_by_product
            })
                    
        order.customer_name = customer_name if customer_name else None
        order.customer_email = customer_email if customer_email else None
        order.customer_phone = customer_phone if customer_phone else None
        order.customer_address = customer_address if customer_address else None
        order.status = status
        order.customer_name = customer_name if customer_name else None
        order.customer_email = customer_email if customer_email else None
        order.customer_phone = customer_phone if customer_phone else None
        order.customer_address = customer_address if customer_address else None
        order.status = status
        order.quantity = total_quantity
        order.save()
        messages.success(request, 'Order updated successfully!')
        return redirect('order_list')
    
    # Add calculated totals to order
    total_value = sum(item.total_price for item in order.items.all())
    total_profit = sum(item.total_profit for item in order.items.all())
    order.calculated_total_value = total_value
    order.calculated_total_profit = total_profit
    
    return render(request, 'edit_order.html', {
        'order': order,
        'products': products,
        'order_items': order_items,
        'inventory_by_product': inventory_by_product
    })


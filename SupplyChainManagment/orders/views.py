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
    
    inventory = {item.product.id: item.quantity for item in InventoryItem.objects.all()}
    inventory_items = {item.product.id: item for item in InventoryItem.objects.all()}
    inventory_units = {item.product.id: item.get_unit_display() for item in InventoryItem.objects.all()}
    if request.method == 'POST':
        status = request.POST.get('status', 'pending')
        order_date_str = request.POST.get('order_date')
        customer_name = request.POST.get('customer_name', 'Walk-in Customer')
        
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
            status=status,
            ordered_by=request.user,
            quantity=0,  # Will update after adding items
            product=products.first(),  # Dummy, not used for multi-product
            order_date=order_date
        )
        total_quantity = 0
        total_order_value = 0
        total_profit = 0
        
        for product in products:
            qty = int(request.POST.get(f'quantity_{product.id}', 0))
            if qty > 0:
                # Create OrderItem with selling price
                order_item = OrderItem.objects.create(
                    order=order, 
                    product=product, 
                    quantity=qty,
                    unit_selling_price=product.selling_price,
                    unit_cost_price=product.cost_price
                )
                
                total_order_value += order_item.total_price
                total_profit += order_item.total_profit
                
                # Subtract from inventory
                try:
                    inv_item = InventoryItem.objects.get(product=product)
                    if inv_item.quantity >= qty:
                        inv_item.quantity -= qty
                        inv_item.save()
                    else:
                        order.delete()
                        messages.error(request, f'Not enough inventory for {product.name}.')
                        return render(request, 'add_order.html', {'products': products, 'inventory': inventory, 'inventory_items': inventory_items, 'inventory_units': inventory_units})
                except InventoryItem.DoesNotExist:
                    order.delete()
                    messages.error(request, f'No inventory record for {product.name}.')
                    return render(request, 'add_order.html', {'products': products, 'inventory': inventory, 'inventory_items': inventory_items, 'inventory_units': inventory_units})
                total_quantity += qty
        if total_quantity == 0:
            order.delete()
            messages.error(request, 'Please enter quantity for at least one product.')
            return render(request, 'add_order.html', {'products': products, 'inventory': inventory, 'inventory_items': inventory_items, 'inventory_units': inventory_units})
        
        order.quantity = total_quantity
        order.save()
        
        # Send real-time toast notification
        notify_new_order(request, order)
        
        # Success message with profit information
        messages.success(request, f'Order placed successfully! Total Value: ${total_order_value:.2f}, Expected Profit: ${total_profit:.2f}')
        request.session['show_success'] = True
        return redirect('order_list')
    return render(request, 'add_order.html', {'products': products, 'inventory': inventory, 'inventory_items': inventory_items, 'inventory_units': inventory_units})

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
    order_items = {item.product.id: item.quantity for item in order.items.all()}
    inventory = {item.product.id: item.quantity for item in InventoryItem.objects.all()}
    inventory_items = {item.product.id: item for item in InventoryItem.objects.all()}
    inventory_units = {item.product.id: item.get_unit_display() for item in InventoryItem.objects.all()}
    
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        status = request.POST.get('status', 'pending')
        
        total_quantity = 0
        for product in products:
            qty = int(request.POST.get(f'quantity_{product.id}', 0))
            existing_item = order.items.filter(product=product).first()
            old_qty = existing_item.quantity if existing_item else 0
            diff = qty - old_qty
            
            # Update inventory
            try:
                inv_item = InventoryItem.objects.get(product=product)
                inv_item.quantity -= diff
                if inv_item.quantity < 0:
                    messages.error(request, f'Not enough inventory for {product.name}.')
                    return render(request, 'edit_order.html', {
                        'order': order,
                        'products': products,
                        'order_items': order_items,
                        'inventory': inventory,
                        'inventory_items': inventory_items,
                        'inventory_units': inventory_units
                    })
                inv_item.save()
            except InventoryItem.DoesNotExist:
                if qty > 0:
                    messages.error(request, f'No inventory record for {product.name}.')
                    return render(request, 'edit_order.html', {
                        'order': order,
                        'products': products,
                        'order_items': order_items,
                        'inventory': inventory,
                        'inventory_items': inventory_items,
                        'inventory_units': inventory_units
                    })
                    
            if qty > 0:
                if existing_item:
                    existing_item.quantity = qty
                    # Update prices to current selling prices
                    existing_item.unit_selling_price = product.selling_price
                    existing_item.unit_cost_price = product.cost_price
                    existing_item.save()
                else:
                    OrderItem.objects.create(
                        order=order, 
                        product=product, 
                        quantity=qty,
                        unit_selling_price=product.selling_price,
                        unit_cost_price=product.cost_price
                    )
                total_quantity += qty
            else:
                if existing_item:
                    existing_item.delete()
                    
        order.customer_name = customer_name if customer_name else None
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
        'inventory': inventory,
        'inventory_items': inventory_items,
        'inventory_units': inventory_units
    })


from django.shortcuts import render, redirect, get_object_or_404
from .models import Order
from .forms import OrderForm
from django.contrib.auth.decorators import login_required
from products.models import Product
from suppliers.models import Supplier
from .models import OrderItem
from django.contrib import messages
from inventory.models import InventoryItem
from django.utils.timezone import make_aware, is_aware

# Create your views here.



@login_required
def add_order(request):
    products = Product.objects.all()
    suppliers = Supplier.objects.all()
    inventory = {item.product.id: item.quantity for item in InventoryItem.objects.all()}
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        status = request.POST.get('status', 'pending')
        order_date_str = request.POST.get('order_date')
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
        supplier = Supplier.objects.get(id=supplier_id) if supplier_id else None
        order = Order.objects.create(
            supplier=supplier,
            status=status,
            ordered_by=request.user,
            quantity=0,  # Will update after adding items
            product=products.first(),  # Dummy, not used for multi-product
            order_date=order_date
        )
        total_quantity = 0
        for product in products:
            qty = int(request.POST.get(f'quantity_{product.id}', 0))
            if qty > 0:
                OrderItem.objects.create(order=order, product=product, quantity=qty)
                # Subtract from inventory
                try:
                    inv_item = InventoryItem.objects.get(product=product)
                    if inv_item.quantity >= qty:
                        inv_item.quantity -= qty
                        inv_item.save()
                    else:
                        order.delete()
                        messages.error(request, f'Not enough inventory for {product.name}.')
                        return render(request, 'add_order.html', {'products': products, 'suppliers': suppliers, 'inventory': inventory})
                except InventoryItem.DoesNotExist:
                    order.delete()
                    messages.error(request, f'No inventory record for {product.name}.')
                    return render(request, 'add_order.html', {'products': products, 'suppliers': suppliers, 'inventory': inventory})
                total_quantity += qty
        if total_quantity == 0:
            order.delete()
            messages.error(request, 'Please enter quantity for at least one product.')
            return render(request, 'add_order.html', {'products': products, 'suppliers': suppliers, 'inventory': inventory})
        order.quantity = total_quantity
        order.save()
        messages.success(request, 'Order placed successfully!')
        request.session['show_success'] = True
        return redirect('order_list')
    return render(request, 'add_order.html', {'products': products, 'suppliers': suppliers, 'inventory': inventory})

@login_required
def order_list(request):
    orders = Order.objects.all().prefetch_related('items', 'supplier')
    return render(request, 'order_list.html', {'orders': orders})

@login_required
def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    products = Product.objects.all()
    suppliers = Supplier.objects.all()
    order_items = {item.product.id: item.quantity for item in order.items.all()}
    inventory = {item.product.id: item.quantity for item in InventoryItem.objects.all()}
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        status = request.POST.get('status', 'pending')
        supplier = Supplier.objects.get(id=supplier_id) if supplier_id else None
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
                        'suppliers': suppliers,
                        'order_items': order_items,
                        'inventory': inventory
                    })
                inv_item.save()
            except InventoryItem.DoesNotExist:
                if qty > 0:
                    messages.error(request, f'No inventory record for {product.name}.')
                    return render(request, 'edit_order.html', {
                        'order': order,
                        'products': products,
                        'suppliers': suppliers,
                        'order_items': order_items,
                        'inventory': inventory
                    })
            if qty > 0:
                if existing_item:
                    existing_item.quantity = qty
                    existing_item.save()
                else:
                    OrderItem.objects.create(order=order, product=product, quantity=qty)
                total_quantity += qty
            else:
                if existing_item:
                    existing_item.delete()
        order.supplier = supplier
        order.status = status
        order.quantity = total_quantity
        order.save()
        messages.success(request, 'Order updated successfully!')
        return redirect('order_list')
    return render(request, 'edit_order.html', {
        'order': order,
        'products': products,
        'suppliers': suppliers,
        'order_items': order_items,
        'inventory': inventory
    })


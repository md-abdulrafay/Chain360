from django.shortcuts import render, redirect, get_object_or_404
from .models import Shipment
from .forms import ShipmentForm
from django.contrib.auth.decorators import login_required
from orders.models import Order
from django.contrib import messages
from theme.notification_utils import notify_shipment_dispatched

@login_required
def shipment_list(request):
    # Only staff and admin can see shipments (customer orders)
    # Suppliers should not see customer shipments as these are internal operations
    if request.user.role not in ['staff', 'admin']:
        context = {
            'error_title': 'Access Denied',
            'error_message': 'Customer shipments are only accessible to admin and staff members.',
            'user_role': request.user.role,
            'suggested_action': 'Suppliers manage purchase orders and goods receipts. Please use the Purchase Orders section instead.',
            'dashboard_url': '/dashboard/',
            'dashboard_text': 'Go to Dashboard'
        }
        return render(request, 'error_pages/access_denied.html', context)
    
    # Staff and admin can see all customer shipments
    shipments = Shipment.objects.all()
    return render(request, 'shipment_list.html', {'shipments': shipments})

@login_required
def add_shipment(request):
    # Only staff and admin can create shipments for customer orders
    if request.user.role not in ['staff', 'admin']:
        context = {
            'error_title': 'Access Denied',
            'error_message': 'Only staff and admin can create customer shipments.',
            'user_role': request.user.role,
            'suggested_action': 'Suppliers should focus on purchase orders and goods receipts, not customer shipments.',
            'dashboard_url': '/dashboard/',
            'dashboard_text': 'Go to Dashboard'
        }
        return render(request, 'error_pages/access_denied.html', context)
    
    if request.method == 'POST':
        form = ShipmentForm(request.POST, user=request.user)
        if form.is_valid():
            shipment = form.save()
            
            # Send real-time toast notification
            notify_shipment_dispatched(request, shipment)
            
            messages.success(request, f'Shipment {shipment.tracking_number} created successfully.')
            return redirect('shipment_list')
    else:
        form = ShipmentForm(user=request.user)
    return render(request, 'shipment_add.html', {'form': form})

@login_required
def edit_shipment(request, pk):
    # Only staff and admin can edit customer shipments
    if request.user.role not in ['staff', 'admin']:
        context = {
            'error_title': 'Access Denied',
            'error_message': 'Only staff and admin can edit customer shipments.',
            'user_role': request.user.role,
            'suggested_action': 'Suppliers manage purchase orders and goods receipts, not customer shipments.',
            'dashboard_url': '/dashboard/',
            'dashboard_text': 'Go to Dashboard'
        }
        return render(request, 'error_pages/access_denied.html', context)
    
    shipment = get_object_or_404(Shipment, pk=pk)
    
    if request.method == 'POST':
        form = ShipmentForm(request.POST, instance=shipment, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Shipment {shipment.tracking_number} updated successfully.')
            return redirect('shipment_list')
    else:
        form = ShipmentForm(instance=shipment, user=request.user)
    return render(request, 'shipment_edit.html', {'form': form})


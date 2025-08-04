from django.shortcuts import render, redirect, get_object_or_404
from .models import Supplier
from .forms import SupplierForm
from .supplier_registration_forms import SupplierRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from theme.notification_utils import notify_supplier_registered

# Create your views here.


@login_required
def supplier_list(request):
    # Filter suppliers based on user role
    if request.user.role == 'supplier':
        # Suppliers can only see their own record
        try:
            suppliers = Supplier.objects.filter(user=request.user)
        except:
            suppliers = Supplier.objects.none()  # Return empty queryset if no supplier record
    elif request.user.role in ['admin', 'staff']:
        # Admin and staff can see all suppliers
        suppliers = Supplier.objects.all()
    else:
        # Other roles get empty queryset
        suppliers = Supplier.objects.none()
    
    return render(request, 'supplier_list.html', {'suppliers': suppliers})

@login_required
def add_supplier(request):
    # Only staff/admin can access this. For new supplier registration, redirect to register_supplier
    if request.user.role not in ['staff', 'admin']:
        messages.error(request, 'You do not have permission to add suppliers directly.')
        return redirect('supplier_list')
        
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully!')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'add_supplier.html', {'form': form})

def register_supplier(request):
    """Public registration for new suppliers"""
    if request.method == 'POST':
        form = SupplierRegistrationForm(request.POST)
        if form.is_valid():
            user, supplier = form.save()
            login(request, user)  # Auto-login the new supplier
            
            # Send notification to admin/staff about new supplier registration
            # We'll send this to the session and show it to admin users when they login
            notify_supplier_registered(request, supplier)
            
            messages.success(request, f'Welcome {supplier.name}! Your supplier account has been created successfully.')
            return redirect('dashboard')  # Will redirect to supplier dashboard via users/views.py
    else:
        form = SupplierRegistrationForm()
    
    return render(request, 'register_supplier.html', {'form': form})

@login_required
def supplier_dashboard(request):
    """Dashboard specifically for supplier users"""
    if request.user.role != 'supplier':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    try:
        supplier = Supplier.objects.get(user=request.user)
        # Get supplier's purchase orders, not customer orders
        from purchases.models import PurchaseOrder, PurchaseInvoice, GoodsReceipt
        from orders.models import Order
        from invoices.models import Invoice
        from shipments.models import Shipment
        
        # Get purchase orders for this supplier
        purchase_orders = PurchaseOrder.objects.filter(supplier=supplier).order_by('-order_date')
        purchase_invoices = PurchaseInvoice.objects.filter(purchase_order__supplier=supplier).order_by('-invoice_date')
        goods_receipts = GoodsReceipt.objects.filter(purchase_order__supplier=supplier).order_by('-received_date')
        
        # For customer orders, invoices, and shipments, we could show orders created by this supplier user
        # or we could show none if suppliers shouldn't see customer orders
        customer_orders = Order.objects.filter(ordered_by=request.user).order_by('-order_date') if hasattr(request.user, 'order_set') else Order.objects.none()
        customer_invoices = Invoice.objects.filter(order__ordered_by=request.user).order_by('-invoice_date') if customer_orders.exists() else Invoice.objects.none()
        customer_shipments = Shipment.objects.filter(order__ordered_by=request.user).order_by('-dispatch_date') if customer_orders.exists() else Shipment.objects.none()
        
        # Add supplier-specific context to request for dashboard
        request.supplier_context = {
            'supplier': supplier,
            'supplier_purchase_orders': purchase_orders,
            'supplier_purchase_invoices': purchase_invoices,
            'supplier_goods_receipts': goods_receipts,
            'supplier_customer_orders': customer_orders,
            'supplier_customer_invoices': customer_invoices,
            'supplier_customer_shipments': customer_shipments,
            'total_purchase_orders': purchase_orders.count(),
            'pending_purchase_orders': purchase_orders.filter(status='draft').count(),
            'total_purchase_invoices': purchase_invoices.count(),
            'unpaid_purchase_invoices': purchase_invoices.filter(payment_status='pending').count(),
            'unpaid_customer_invoices': customer_invoices.filter(payment_status='unpaid').count() if customer_invoices.exists() else 0,
            'is_supplier_dashboard': True,
        }
        
        # Use the existing dashboard view but with supplier context
        from theme.views import dashboard
        return dashboard(request)
        
    except Supplier.DoesNotExist:
        messages.error(request, 'No supplier record found for your account.')
        return redirect('dashboard')

@login_required
def edit_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'edit_supplier.html', {'form': form})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import PurchaseOrder, PurchaseOrderItem, PurchaseInvoice, GoodsReceipt, GoodsReceiptItem
from .forms import (PurchaseOrderForm, PurchaseOrderItemFormSet, PurchaseInvoiceForm, 
                   GoodsReceiptForm, QuickPurchaseForm)
from suppliers.models import Supplier
from suppliers.decorators import staff_or_admin_required, supplier_required
from products.models import Product
from inventory.models import InventoryItem

@staff_or_admin_required
def purchase_dashboard(request):
    """Dashboard showing purchase overview - Staff/Admin only"""
    context = {
        'total_pos': PurchaseOrder.objects.count(),
        'pending_pos': PurchaseOrder.objects.filter(status__in=['draft', 'sent']).count(),
        'pending_receipts': PurchaseOrder.objects.filter(status='confirmed').count(),
        'pending_invoices': PurchaseInvoice.objects.filter(payment_status='pending').count(),
        'recent_pos': PurchaseOrder.objects.all()[:5],
        'recent_receipts': GoodsReceipt.objects.all()[:5],
    }
    return render(request, 'purchases/dashboard.html', context)

@login_required
def purchase_order_list(request):
    """List purchase orders with role-based filtering"""
    pos = PurchaseOrder.objects.all().select_related('supplier', 'created_by')
    
    # Role-based filtering
    if request.user.role == 'supplier':
        # Suppliers can only see orders assigned to them
        try:
            supplier = Supplier.objects.get(user=request.user)
            pos = pos.filter(supplier=supplier)
        except Supplier.DoesNotExist:
            messages.error(request, 'No supplier record found for your account!')
            return redirect('dashboard')
    # Admin and staff can see all orders (no additional filtering needed)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        pos = pos.filter(status=status)
    
    # Filter by supplier (only for admin/staff)
    supplier_id = request.GET.get('supplier')
    if supplier_id and request.user.role in ['admin', 'staff']:
        pos = pos.filter(supplier_id=supplier_id)
    
    # Search
    search = request.GET.get('search')
    if search:
        pos = pos.filter(
            Q(po_number__icontains=search) |
            Q(supplier__name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(pos, 10)
    page_number = request.GET.get('page')
    pos = paginator.get_page(page_number)
    
    # Only show supplier filter to admin/staff
    suppliers = Supplier.objects.all() if request.user.role in ['admin', 'staff'] else []
    
    context = {
        'purchase_orders': pos,
        'suppliers': suppliers,
        'status_choices': PurchaseOrder.STATUS_CHOICES,
        'user_role': request.user.role,
    }
    return render(request, 'purchases/purchase_order_list.html', context)

@staff_or_admin_required
def create_purchase_order(request):
    """Create a new purchase order - Staff/Admin only"""
    products = Product.objects.all()
    suppliers = Supplier.objects.all()
    
    # Get current inventory for display with units
    inventory_data = {}
    inventory_units = {}
    for item in InventoryItem.objects.select_related('product'):
        inventory_data[item.product.id] = item.quantity
        inventory_units[item.product.id] = item.get_unit_display()
    
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        status = request.POST.get('status', 'draft')
        expected_delivery_date = request.POST.get('expected_delivery_date')
        notes = request.POST.get('notes', '')
        
        # Validate supplier
        if not supplier_id:
            messages.error(request, 'Please select a supplier.')
            return render(request, 'purchases/create_purchase_order.html', {
                'products': products, 
                'suppliers': suppliers,
                'inventory': inventory_data,
                'inventory_units': inventory_units
            })
        
        supplier = get_object_or_404(Supplier, id=supplier_id)
        
        # Create purchase order
        po = PurchaseOrder.objects.create(
            supplier=supplier,
            created_by=request.user,
            expected_delivery_date=expected_delivery_date if expected_delivery_date else None,
            status=status,
            notes=notes
        )
        
        # Process products and quantities
        total_amount = 0
        items_added = 0
        
        for product in products:
            qty = int(request.POST.get(f'quantity_{product.id}', 0))
            unit_price = float(request.POST.get(f'unit_price_{product.id}', 0))
            
            if qty > 0 and unit_price > 0:
                # Create purchase order item
                po_item = PurchaseOrderItem.objects.create(
                    purchase_order=po,
                    product=product,
                    quantity_ordered=qty,
                    unit_price=unit_price
                )
                total_amount += po_item.total_price
                items_added += 1
        
        if items_added == 0:
            po.delete()
            messages.error(request, 'Please add at least one product with quantity and price.')
            return render(request, 'purchases/create_purchase_order.html', {
                'products': products, 
                'suppliers': suppliers,
                'inventory': inventory_data,
                'inventory_units': inventory_units
            })
        
        # Update total amount
        po.total_amount = total_amount
        po.save()
        
        messages.success(request, f'Purchase Order {po.po_number} created successfully with {items_added} items!')
        return redirect('purchases:purchase_order_detail', pk=po.pk)
    
    context = {
        'products': products,
        'suppliers': suppliers,
        'inventory': inventory_data,
        'inventory_units': inventory_units,
    }
    return render(request, 'purchases/create_purchase_order.html', context)

@staff_or_admin_required
def quick_purchase(request):
    """Quick purchase form for single item - Staff/Admin only"""
    if request.method == 'POST':
        form = QuickPurchaseForm(request.POST)
        if form.is_valid():
            # Create PO
            po = PurchaseOrder.objects.create(
                supplier=form.cleaned_data['supplier'],
                created_by=request.user,
                expected_delivery_date=form.cleaned_data['expected_delivery_date'],
                status='draft'
            )
            
            # Create PO Item
            PurchaseOrderItem.objects.create(
                purchase_order=po,
                product=form.cleaned_data['product'],
                quantity_ordered=form.cleaned_data['quantity'],
                unit_price=form.cleaned_data['unit_price']
            )
            
            po.calculate_total()
            messages.success(request, f'Quick Purchase Order {po.po_number} created successfully!')
            return redirect('purchases:purchase_order_detail', pk=po.pk)
    else:
        form = QuickPurchaseForm()
    
    return render(request, 'purchases/quick_purchase.html', {'form': form})

@login_required
def purchase_order_detail(request, pk):
    """View purchase order details with role-based access"""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    
    # Role-based access control
    if request.user.role == 'supplier':
        try:
            supplier = Supplier.objects.get(user=request.user)
            if po.supplier != supplier:
                messages.error(request, 'You can only view your own purchase orders!')
                return redirect('purchases:purchase_order_list')
        except Supplier.DoesNotExist:
            messages.error(request, 'No supplier record found for your account!')
            return redirect('purchases:purchase_order_list')
    
    items = po.items.all().select_related('product')
    invoices = po.invoices.all()
    receipts = po.receipts.all()
    
    # Check if any invoices are paid to prevent duplicate invoice creation
    has_paid_invoices = invoices.filter(payment_status='paid').exists()
    
    context = {
        'po': po,
        'items': items,
        'invoices': invoices,
        'receipts': receipts,
        'user_role': request.user.role,
        'has_paid_invoices': has_paid_invoices,
    }
    return render(request, 'purchases/purchase_order_detail.html', context)

@staff_or_admin_required
def send_to_supplier(request, pk):
    """Send purchase order to supplier - Staff/Admin only"""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if po.status == 'draft':
        po.status = 'sent'
        po.save()
        messages.success(request, f'Purchase Order {po.po_number} sent to supplier!')
    else:
        messages.warning(request, 'Purchase Order is not in draft status!')
    return redirect('purchases:purchase_order_detail', pk=pk)

@login_required
def confirm_purchase_order(request, pk):
    """Confirm purchase order - Suppliers can confirm their own POs, Staff/Admin can confirm any"""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    
    # Check if user is the supplier or staff/admin
    if request.user.role == 'supplier':
        try:
            supplier = Supplier.objects.get(user=request.user)
            if po.supplier != supplier:
                messages.error(request, 'You can only confirm your own purchase orders!')
                return redirect('purchases:purchase_order_list')
        except Supplier.DoesNotExist:
            messages.error(request, 'No supplier record found for your account!')
            return redirect('purchases:purchase_order_list')
    elif request.user.role not in ['staff', 'admin']:
        messages.error(request, 'You do not have permission to confirm purchase orders!')
        return redirect('purchases:purchase_order_list')
    
    if po.status == 'sent':
        po.status = 'confirmed'
        po.save()
        messages.success(request, f'Purchase Order {po.po_number} confirmed!')
    else:
        messages.warning(request, 'Purchase Order is not in sent status!')
    return redirect('purchases:purchase_order_detail', pk=pk)

@staff_or_admin_required
def receive_goods(request, pk):
    """Receive goods from purchase order - Staff/Admin only"""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    
    # Check if PO is in correct status for receiving goods
    if po.status not in ['confirmed', 'partially_received']:
        messages.error(request, f'Cannot receive goods for purchase order in {po.get_status_display()} status. Order must be confirmed by supplier first.')
        return redirect('purchases:purchase_order_detail', pk=pk)
    
    if request.method == 'POST':
        form = GoodsReceiptForm(request.POST)
        if form.is_valid():
            # Check if at least one quantity is entered
            has_quantities = False
            for item in po.items.all():
                received_qty = request.POST.get(f'quantity_{item.id}')
                if received_qty and int(received_qty) > 0:
                    has_quantities = True
                    break
            
            if not has_quantities:
                messages.error(request, 'Please enter at least one quantity to receive.')
                form = GoodsReceiptForm(request.POST)  # Keep form data
            else:
                receipt = form.save(commit=False)
                receipt.purchase_order = po
                receipt.received_by = request.user
                receipt.save()
                
                # Process received items
                for item in po.items.all():
                    received_qty = request.POST.get(f'quantity_{item.id}')
                    if received_qty and int(received_qty) > 0:
                        # Create goods receipt item (this will automatically update inventory and PO item)
                        GoodsReceiptItem.objects.create(
                            goods_receipt=receipt,
                            purchase_order_item=item,
                            quantity_received=int(received_qty)
                        )
                
                # Update PO status
                all_received = all(item.is_fully_received for item in po.items.all())
                if all_received:
                    po.status = 'received'
                else:
                    po.status = 'partially_received'
                po.save()
                
                messages.success(request, f'Goods receipt {receipt.receipt_number} created successfully!')
                return redirect('purchases:purchase_order_detail', pk=pk)
    else:
        form = GoodsReceiptForm()
    
    items = po.items.all().select_related('product')
    # Get recent receipts for this PO
    recent_receipts = po.receipts.all()[:5]
    
    context = {
        'po': po,
        'form': form,
        'items': items,
        'recent_receipts': recent_receipts,
    }
    return render(request, 'purchases/receive_goods.html', context)

@staff_or_admin_required
def create_purchase_invoice(request, pk):
    """Create invoice for purchase order - Staff/Admin only"""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    
    # Check if any paid invoices already exist for this PO
    if po.invoices.filter(payment_status='paid').exists():
        messages.warning(request, f'Purchase Order {po.po_number} already has a paid invoice. No new invoice is needed.')
        return redirect('purchases:purchase_order_detail', pk=pk)
    
    if request.method == 'POST':
        form = PurchaseInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.purchase_order = po
            invoice.save()
            messages.success(request, f'Purchase Invoice {invoice.invoice_number} created successfully!')
            return redirect('purchases:purchase_order_detail', pk=pk)
    else:
        form = PurchaseInvoiceForm(initial={'amount': po.total_amount})
    
    context = {
        'po': po,
        'form': form,
    }
    return render(request, 'purchases/create_invoice.html', context)

@staff_or_admin_required
def purchase_invoice_list(request):
    """List all purchase invoices - Staff/Admin only"""
    invoices = PurchaseInvoice.objects.all().select_related('purchase_order__supplier')
    
    # Filter by payment status
    payment_status = request.GET.get('payment_status')
    if payment_status:
        invoices = invoices.filter(payment_status=payment_status)
    
    # Filter by supplier
    supplier = request.GET.get('supplier')
    if supplier:
        invoices = invoices.filter(purchase_order__supplier_id=supplier)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) |
            Q(supplier_invoice_number__icontains=search) |
            Q(purchase_order__po_number__icontains=search)
        )
    
    # Calculate statistics
    total_invoices = invoices.count()
    pending_count = invoices.filter(payment_status='pending').count()
    overdue_count = invoices.filter(payment_status='overdue').count()
    total_amount = invoices.aggregate(total=Sum('amount'))['total'] or 0
    
    # Get suppliers for filter
    suppliers = Supplier.objects.all()
    
    # Pagination
    paginator = Paginator(invoices, 10)
    page_number = request.GET.get('page')
    invoices = paginator.get_page(page_number)
    
    context = {
        'invoices': invoices,
        'suppliers': suppliers,
        'total_invoices': total_invoices,
        'pending_count': pending_count,
        'overdue_count': overdue_count,
        'total_amount': total_amount,
    }
    return render(request, 'purchases/invoice_list.html', context)

@staff_or_admin_required
def mark_invoice_paid(request, pk):
    """Mark invoice as paid - Staff/Admin only"""
    invoice = get_object_or_404(PurchaseInvoice, pk=pk)
    invoice.payment_status = 'paid'
    invoice.save()
    messages.success(request, f'Invoice {invoice.invoice_number} marked as paid!')
    return redirect('purchases:invoice_list')

@staff_or_admin_required
def goods_receipt_list(request):
    """List all goods receipts - Staff/Admin only"""
    receipts = GoodsReceipt.objects.all().select_related('purchase_order__supplier', 'received_by')
    
    # Filter by date range
    date_range = request.GET.get('date_range')
    if date_range:
        from datetime import datetime, timedelta
        today = datetime.now().date()
        if date_range == 'today':
            receipts = receipts.filter(received_date__date=today)
        elif date_range == 'week':
            start_date = today - timedelta(days=7)
            receipts = receipts.filter(received_date__date__gte=start_date)
        elif date_range == 'month':
            start_date = today.replace(day=1)
            receipts = receipts.filter(received_date__date__gte=start_date)
    
    # Filter by supplier
    supplier = request.GET.get('supplier')
    if supplier:
        receipts = receipts.filter(purchase_order__supplier_id=supplier)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        receipts = receipts.filter(
            Q(receipt_number__icontains=search) |
            Q(purchase_order__po_number__icontains=search)
        )
    
    # Calculate statistics
    from datetime import datetime
    today = datetime.now().date()
    start_of_month = today.replace(day=1)
    
    total_receipts = receipts.count()
    month_receipts = receipts.filter(received_date__date__gte=start_of_month).count()
    total_items = sum(receipt.items.count() for receipt in receipts)
    active_suppliers = receipts.values('purchase_order__supplier').distinct().count()
    
    # Get suppliers for filter
    suppliers = Supplier.objects.all()
    
    # Pagination
    paginator = Paginator(receipts, 10)
    page_number = request.GET.get('page')
    receipts = paginator.get_page(page_number)
    
    context = {
        'receipts': receipts,
        'suppliers': suppliers,
        'total_receipts': total_receipts,
        'month_receipts': month_receipts,
        'total_items': total_items,
        'active_suppliers': active_suppliers,
    }
    return render(request, 'purchases/receipt_list.html', context)

@staff_or_admin_required
def goods_receipt_detail(request, pk):
    """View goods receipt details - Staff/Admin only"""
    receipt = get_object_or_404(GoodsReceipt, pk=pk)
    items = receipt.items.all().select_related('purchase_order_item__product')
    
    context = {
        'receipt': receipt,
        'items': items,
        'po': receipt.purchase_order,
    }
    return render(request, 'purchases/receipt_detail.html', context)

# API views for AJAX requests
@login_required
def get_product_price(request):
    """Get product price for AJAX requests - returns cost price for purchase orders"""
    product_id = request.GET.get('product_id')
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
            # For purchase orders, use cost_price (what we pay to suppliers)
            # If cost_price is not set, fall back to the legacy price field
            price = product.cost_price
            return JsonResponse({'price': str(price)})
        except Product.DoesNotExist:
            pass
    return JsonResponse({'price': '0.00'})

@supplier_required
def supplier_dashboard(request):
    """Dashboard for suppliers showing their purchase orders"""
    supplier = request.supplier  # Added by decorator
    
    # Get purchase orders for this supplier
    pos = PurchaseOrder.objects.filter(supplier=supplier)
    
    context = {
        'total_pos': pos.count(),
        'pending_confirmations': pos.filter(status='sent').count(),
        'confirmed_pos': pos.filter(status='confirmed').count(),
        'completed_pos': pos.filter(status='received').count(),
        'recent_pos': pos.order_by('-created_date')[:5],
        'supplier': supplier,
    }
    return render(request, 'purchases/supplier_dashboard.html', context)

@staff_or_admin_required
def download_purchase_invoice_pdf(request, pk):
    """Download purchase invoice as PDF - Staff/Admin only"""
    invoice = get_object_or_404(PurchaseInvoice, pk=pk)
    po = invoice.purchase_order
    supplier = po.supplier
    po_items = po.items.all()
    
    # Calculate tax and delivery (you can customize this logic)
    subtotal = sum(item.total_price for item in po_items)
    delivery = 100  # Fixed delivery cost
    tax = invoice.amount - subtotal - delivery if invoice.amount > subtotal else 0
    
    template_path = 'purchases/purchase_invoice_pdf.html'
    context = {
        'invoice': invoice,
        'po': po,
        'supplier': supplier,
        'items': po_items,
        'subtotal': subtotal,
        'tax': tax,
        'delivery': delivery,
    }
    
    template = get_template(template_path)
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="purchase_invoice_{invoice.invoice_number}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

from django.shortcuts import render, redirect, get_object_or_404
from .models import Invoice
from .forms import InvoiceForm
from django.contrib.auth.decorators import login_required
from orders.models import Order, OrderItem
from decimal import Decimal
from django.http import HttpResponse
from django.template.loader import get_template
import io
from xhtml2pdf import pisa
from theme.views import get_notifications
from django.contrib import messages
from theme.notification_utils import notify_invoice_paid

@login_required
def invoice_list(request):
    # All users can see all invoices for customer orders
    invoices = Invoice.objects.all()
    return render(request, 'invoice_list.html', {'invoices': invoices})

@login_required
def add_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST, user=request.user)
        if form.is_valid():
            invoice = form.save(commit=False)
            order = invoice.order
            
            # Calculate amount from order items if present, else from order
            order_items = OrderItem.objects.filter(order=order)
            if order_items.exists():
                amount = sum(item.unit_selling_price * item.quantity for item in order_items)
            else:
                amount = order.product.selling_price * order.quantity
            tax = amount * Decimal('0.05')
            delivery = 100
            invoice.amount = amount + tax + delivery
            invoice.save()
            return redirect('invoice_list')
    else:
        form = InvoiceForm(user=request.user)
    notifications = get_notifications()
    return render(request, 'add_invoice.html', {'form': form, 'notifications': notifications})

@login_required
def edit_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Check if supplier user can only edit invoices for their orders
    if request.user.role == 'supplier':
        try:
            from suppliers.models import Supplier
            supplier = Supplier.objects.get(user=request.user)
            if invoice.order.supplier != supplier:
                messages.error(request, 'You can only edit invoices for your own orders.')
                return redirect('invoice_list')
        except Supplier.DoesNotExist:
            messages.error(request, 'Supplier record not found.')
            return redirect('invoice_list')
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice, user=request.user)
        if form.is_valid():
            # Check if payment status changed to 'paid'
            old_payment_status = Invoice.objects.get(pk=invoice.pk).payment_status
            invoice = form.save(commit=False)
            order = invoice.order
            order_items = OrderItem.objects.filter(order=order)
            if order_items.exists():
                amount = sum(item.product.selling_price * item.quantity for item in order_items)
            else:
                amount = order.product.selling_price * order.quantity
            tax = amount * Decimal('0.05')
            delivery = 100
            invoice.amount = amount + tax + delivery
            invoice.save()
            
            # Send notification if invoice was just paid
            if old_payment_status != 'paid' and invoice.payment_status == 'paid':
                notify_invoice_paid(request, invoice)
            
            return redirect('invoice_list')
    else:
        form = InvoiceForm(instance=invoice, user=request.user)
    return render(request, 'edit_invoice.html', {'form': form})

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    order = invoice.order
    customer_name = order.customer_name or "Walk-in Customer"
    order_items = OrderItem.objects.filter(order=order)
    if order_items.exists():
        products = order_items
        subtotal = sum(item.total_price for item in order_items)
    else:
        products = [order]
        subtotal = order.product.selling_price * order.quantity
    
    # Calculate 5% tax on subtotal
    tax = subtotal * Decimal('0.05')
    
    return render(request, 'invoice_detail.html', {
        'invoice': invoice,
        'order': order,
        'customer_name': customer_name,
        'products': products,
        'subtotal': subtotal,
        'tax': tax,
        'delivery': 100,
    })

@login_required
def download_invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    order = invoice.order
    customer_name = order.customer_name or "Walk-in Customer"
    order_items = OrderItem.objects.filter(order=order)
    if order_items.exists():
        products = order_items
        subtotal = sum(item.total_price for item in order_items)
    else:
        products = [order]
        subtotal = order.product.selling_price * order.quantity
    
    # Calculate 5% tax on subtotal
    tax = subtotal * Decimal('0.05')
    delivery = 100
    template_path = 'invoice_detail_pdf.html'
    context = {
        'invoice': invoice,
        'order': order,
        'customer_name': customer_name,
        'products': products,
        'subtotal': subtotal,
        'tax': tax,
        'delivery': delivery,
    }
    template = get_template(template_path)
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

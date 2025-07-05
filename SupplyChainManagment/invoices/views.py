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

@login_required
def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, 'invoice_list.html', {'invoices': invoices})

@login_required
def add_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            order = invoice.order
            # Calculate amount from order items if present, else from order
            order_items = OrderItem.objects.filter(order=order)
            if order_items.exists():
                amount = sum(item.product.price * item.quantity for item in order_items)
            else:
                amount = order.product.price * order.quantity
            tax = amount * Decimal('0.05')
            delivery = 100
            invoice.amount = amount + tax + delivery
            invoice.save()
            return redirect('invoice_list')
    else:
        form = InvoiceForm()
    notifications = get_notifications()
    return render(request, 'add_invoice.html', {'form': form, 'notifications': notifications})

@login_required
def edit_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            invoice = form.save(commit=False)
            order = invoice.order
            order_items = OrderItem.objects.filter(order=order)
            if order_items.exists():
                amount = sum(item.product.price * item.quantity for item in order_items)
            else:
                amount = order.product.price * order.quantity
            tax = amount * Decimal('0.05')
            delivery = 100
            invoice.amount = amount + tax + delivery
            invoice.save()
            return redirect('invoice_list')
    else:
        form = InvoiceForm(instance=invoice)
    return render(request, 'edit_invoice.html', {'form': form})

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    order = invoice.order
    supplier = order.supplier
    order_items = OrderItem.objects.filter(order=order)
    if order_items.exists():
        products = order_items
    else:
        products = [order]
    return render(request, 'invoice_detail.html', {
        'invoice': invoice,
        'order': order,
        'supplier': supplier,
        'products': products,
        'tax': invoice.amount - 100 - (sum(item.product.price * item.quantity for item in order_items) if order_items.exists() else order.product.price * order.quantity),
        'delivery': 100,
    })

@login_required
def download_invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    order = invoice.order
    supplier = order.supplier
    order_items = OrderItem.objects.filter(order=order)
    if order_items.exists():
        products = order_items
    else:
        products = [order]
    tax = invoice.amount - 100 - (sum(item.product.price * item.quantity for item in order_items) if order_items.exists() else order.product.price * order.quantity)
    delivery = 100
    template_path = 'invoice_detail_pdf.html'
    context = {
        'invoice': invoice,
        'order': order,
        'supplier': supplier,
        'products': products,
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

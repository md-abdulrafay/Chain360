from django.shortcuts import render
from orders.models import Order, OrderItem
from shipments.models import Shipment
from products.models import Product
from suppliers.models import Supplier
from inventory.models import InventoryItem
from invoices.models import Invoice
from django.db.models import Count, Sum, F, FloatField
from django.utils.timezone import now
from datetime import timedelta
from django.db.models.functions import TruncDay
import calendar
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.utils.dateparse import parse_date
import datetime
from django.utils.timezone import make_aware, is_aware

def ensure_aware(dt):
    if dt is None:
        return None
    import datetime as py_datetime
    if isinstance(dt, py_datetime.date) and not isinstance(dt, py_datetime.datetime):
        # It's a date, not a datetime, so just return as is
        return dt
    from django.utils.timezone import is_aware, make_aware
    if is_aware(dt):
        return dt
    return make_aware(dt)

def get_notifications():
    notifications = []
    # New Orders (last 7 days)
    new_orders = Order.objects.filter(order_date__gte=now().date()-timedelta(days=7)).order_by('-order_date')
    for order in new_orders:
        notifications.append({
            'type': 'order',
            'icon': 'fa-birthday-cake',
            'title': f'New Order #{order.id}',
            'text': f'Order placed by {order.ordered_by.username}',
            'time': order.order_date.strftime('%d %b') if order.order_date else '',
            'timestamp': ensure_aware(order.order_date) if order.order_date else None,
            'order_id': order.id
        })
    # Order Shipments placed (last 7 days)
    new_shipments = Shipment.objects.filter(dispatch_date__gte=now().date()-timedelta(days=7)).order_by('-dispatch_date')
    for shipment in new_shipments:
        notifications.append({
            'type': 'shipment',
            'icon': 'fa-shipping-fast',
            'title': f'Shipment for Order #{shipment.order.id}',
            'text': f'Shipment dispatched: {shipment.tracking_number}',
            'time': shipment.dispatch_date.strftime('%d %b') if shipment.dispatch_date else '',
            'timestamp': ensure_aware(shipment.dispatch_date) if shipment.dispatch_date else now(),
            'order_id': shipment.order.id
        })
    # New Products added (last 7 days)
    new_products = Product.objects.filter().order_by('-id')[:5]
    for product in new_products:
        notifications.append({
            'type': 'product',
            'icon': 'fa-box',
            'title': f'New Product: {product.name}',
            'text': f'Added by {product.created_by.username}',
            'time': product.created_at.strftime('%d %b') if hasattr(product, 'created_at') and product.created_at else '',
            'timestamp': product.created_at if hasattr(product, 'created_at') and product.created_at else now(),
            'order_id': None
        })
    # Inventory low (quantity < 5)
    low_inventory = InventoryItem.objects.filter(quantity__lt=5)
    for item in low_inventory:
        notifications.append({
            'type': 'inventory',
            'icon': 'fa-exclamation-triangle',
            'title': f'Low Inventory: {item.product.name}',
            'text': f'Only {item.quantity} left in stock',
            'time': '',
            'timestamp': now(),
            'order_id': None
        })
    # Invoice paid (last 7 days)
    paid_invoices = Invoice.objects.filter(payment_status='paid', invoice_date__gte=now().date()-timedelta(days=7))
    for invoice in paid_invoices:
        notifications.append({
            'type': 'invoice',
            'icon': 'fa-file-invoice-dollar',
            'title': f'Invoice Paid for Order #{invoice.order.id}',
            'text': f'Invoice #{invoice.invoice_number} paid',
            'time': invoice.invoice_date.strftime('%d %b'),
            'timestamp': ensure_aware(invoice.invoice_date),
            'order_id': invoice.order.id
        })
    # New supplier added (last 7 days)
    new_suppliers = Supplier.objects.filter().order_by('-id')[:5]
    for supplier in new_suppliers:
        notifications.append({
            'type': 'supplier',
            'icon': 'fa-user-plus',
            'title': f'New Supplier: {supplier.name}',
            'text': f'Contact: {supplier.contact_person}',
            'time': '',
            'timestamp': now(),
            'order_id': None
        })
    import datetime as py_datetime
    from django.utils.timezone import is_aware, make_aware, get_current_timezone
    def to_datetime(ts):
        if ts is None:
            ts = now()
        if isinstance(ts, py_datetime.date) and not isinstance(ts, py_datetime.datetime):
            ts = py_datetime.datetime.combine(ts, py_datetime.time.min)
        if not is_aware(ts):
            ts = make_aware(ts, get_current_timezone())
        return ts
    notifications = sorted(
        notifications,
        key=lambda n: to_datetime(n['timestamp']),
        reverse=True
    )
    return notifications

def dashboard(request):
    total_orders = Order.objects.count()
    total_shipments = Shipment.objects.count()
    delivered_shipments = Shipment.objects.filter(status='delivered').count()
    total_products = Product.objects.count()

    fulfillment_rate = (
        (delivered_shipments / total_shipments) * 100
        if total_shipments > 0 else 0
    )

    top_products = (
        Order.objects.values('product__name')
        .annotate(count=Count('product'))
        .order_by('-count')[:5]
    )

    top_suppliers = (
        Order.objects.values('supplier__name')
        .annotate(count=Count('supplier'))
        .order_by('-count')[:5]
    )

    today = now().date()
    yesterday = today - timedelta(days=1)
    start_of_week = today - timedelta(days=today.weekday())
    start_of_last_week = start_of_week - timedelta(days=7)
    end_of_last_week = start_of_week - timedelta(days=1)
    first_day_this_month = today.replace(day=1)
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    start_90_days_ago = today - timedelta(days=89)
    last_year = today.year - 1

    days_in_month = (today.replace(day=calendar.monthrange(today.year, today.month)[1]).day)

    def get_sales_and_orders(start_date, end_date):
        qs = Order.objects.filter(order_date__gte=start_date, order_date__lte=end_date)
        sales = qs.annotate(revenue=F('quantity') * F('product__price')).aggregate(total=Sum('revenue', output_field=FloatField()))['total'] or 0
        orders = qs.count()
        return sales, orders

    def get_sales_last_year(start_date, end_date):
        delta = end_date - start_date
        start = start_date.replace(year=last_year)
        end = start + delta
        qs = Order.objects.filter(order_date__gte=start, order_date__lte=end)
        sales = qs.annotate(revenue=F('quantity') * F('product__price')).aggregate(total=Sum('revenue', output_field=FloatField()))['total'] or 0
        return sales

    sales_today, orders_today = get_sales_and_orders(today, today)
    sales_today_last_year = get_sales_last_year(today, today)
    sales_yesterday, orders_yesterday = get_sales_and_orders(yesterday, yesterday)
    sales_yesterday_last_year = get_sales_last_year(yesterday, yesterday)
    sales_last_week, orders_last_week = get_sales_and_orders(start_of_last_week, end_of_last_week)
    sales_last_week_last_year = get_sales_last_year(start_of_last_week, end_of_last_week)
    sales_last_month, orders_last_month = get_sales_and_orders(first_day_last_month, last_day_last_month)
    sales_last_month_last_year = get_sales_last_year(first_day_last_month, last_day_last_month)
    sales_90_days, orders_90_days = get_sales_and_orders(start_90_days_ago, today)
    sales_90_days_last_year = get_sales_last_year(start_90_days_ago, today)

    # Sales this month (revenue)
    sales_this_month = Order.objects.filter(order_date__gte=first_day_this_month).annotate(
        revenue=F('quantity') * F('product__price')
    ).aggregate(total=Sum('revenue', output_field=FloatField()))['total'] or 0
    # Sales last month (revenue)
    sales_last_month = Order.objects.filter(order_date__gte=first_day_last_month, order_date__lte=last_day_last_month).annotate(
        revenue=F('quantity') * F('product__price')
    ).aggregate(total=Sum('revenue', output_field=FloatField()))['total'] or 0
    # % more sales in comparison to last month
    if sales_last_month > 0:
        percent_more_sales = ((sales_this_month - sales_last_month) / sales_last_month) * 100
    else:
        percent_more_sales = 100 if sales_this_month > 0 else 0
    # Revenue per sale this month and last month
    orders_this_month = Order.objects.filter(order_date__gte=first_day_this_month).count()
    orders_last_month = Order.objects.filter(order_date__gte=first_day_last_month, order_date__lte=last_day_last_month).count()
    revenue_per_sale_this_month = sales_this_month / orders_this_month if orders_this_month > 0 else 0
    revenue_per_sale_last_month = sales_last_month / orders_last_month if orders_last_month > 0 else 0
    if revenue_per_sale_last_month > 0:
        percent_revenue_per_sale = ((revenue_per_sale_this_month - revenue_per_sale_last_month) / revenue_per_sale_last_month) * 100
    else:
        percent_revenue_per_sale = 100 if revenue_per_sale_this_month > 0 else 0

    last_month = today - timedelta(days=30)
    recent_orders = Order.objects.filter(order_date__gte=last_month).order_by('-order_date')
    total_item_sales = Order.objects.aggregate(total=Sum('quantity'))['total'] or 0

    # Get sales per day for this month
    sales_per_day_qs = (
        Order.objects.filter(order_date__gte=first_day_this_month, order_date__lte=today)
        .annotate(day=TruncDay('order_date'))
        .values('day')
        .annotate(sales=Sum(F('quantity') * F('product__price'), output_field=FloatField()))
        .order_by('day')
    )
    sales_per_day = [0] * days_in_month
    for entry in sales_per_day_qs:
        day = entry['day'].day
        sales_per_day[day-1] = round(entry['sales'] or 0, 2)

    # Get product sales for this month (sync with OrderItem, not just Order)
    from orders.models import OrderItem
    order_ids = Order.objects.filter(order_date__gte=first_day_this_month).values_list('id', flat=True)
    product_sales_qs = OrderItem.objects.filter(order_id__in=order_ids) \
        .values('product__name') \
        .annotate(total_sold=Sum('quantity')) \
        .order_by('-total_sold')
    product_names = [entry['product__name'] for entry in product_sales_qs]
    sales_counts = [entry['total_sold'] for entry in product_sales_qs]

    context = {
        'total_orders': total_orders,
        'total_item_sales': total_item_sales,
        'total_shipments': total_shipments,
        'total_products': total_products,
        'fulfillment_rate': round(fulfillment_rate, 2),
        'top_products': top_products,
        'top_suppliers': top_suppliers,
        'recent_orders': recent_orders,
        'sales_today': round(sales_today, 2),
        'orders_today': orders_today,
        'sales_today_last_year': round(sales_today_last_year, 2),
        'sales_yesterday': round(sales_yesterday, 2),
        'orders_yesterday': orders_yesterday,
        'sales_yesterday_last_year': round(sales_yesterday_last_year, 2),
        'sales_last_week': round(sales_last_week, 2),
        'orders_last_week': orders_last_week,
        'sales_last_week_last_year': round(sales_last_week_last_year, 2),
        'sales_last_month': round(sales_last_month, 2),
        'orders_last_month': orders_last_month,
        'sales_last_month_last_year': round(sales_last_month_last_year, 2),
        'sales_90_days': round(sales_90_days, 2),
        'orders_90_days': orders_90_days,
        'sales_90_days_last_year': round(sales_90_days_last_year, 2),
        'sales_this_month': round(sales_this_month, 2),
        'percent_more_sales': round(percent_more_sales, 2),
        'percent_revenue_per_sale': round(percent_revenue_per_sale, 2),
        'sales_per_day': sales_per_day,
        'days_in_month': list(range(1, days_in_month+1)),
        'product_names': json.dumps(product_names, cls=DjangoJSONEncoder),
        'sales_counts': json.dumps(sales_counts, cls=DjangoJSONEncoder),
        'notifications': get_notifications(),
    }

    return render(request, 'dashboard.html', context)

def dashboard_1(request):
    total_orders = Order.objects.count()
    total_shipments = Shipment.objects.count()
    delivered_shipments = Shipment.objects.filter(status='delivered').count()
    total_products = Product.objects.count()

    fulfillment_rate = (
        (delivered_shipments / total_shipments) * 100
        if total_shipments > 0 else 0
    )

    top_products = (
        Order.objects.values('product__name')
        .annotate(count=Count('product'))
        .order_by('-count')[:5]
    )

    top_suppliers = (
        Order.objects.values('supplier__name')
        .annotate(count=Count('supplier'))
        .order_by('-count')[:5]
    )

    today = now().date()
    yesterday = today - timedelta(days=1)
    start_of_week = today - timedelta(days=today.weekday())
    start_of_last_week = start_of_week - timedelta(days=7)
    end_of_last_week = start_of_week - timedelta(days=1)
    first_day_this_month = today.replace(day=1)
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    start_90_days_ago = today - timedelta(days=89)
    last_year = today.year - 1

    days_in_month = (today.replace(day=calendar.monthrange(today.year, today.month)[1]).day)

    def get_sales_and_orders(start_date, end_date):
        qs = Order.objects.filter(order_date__gte=start_date, order_date__lte=end_date)
        sales = qs.annotate(revenue=F('quantity') * F('product__price')).aggregate(total=Sum('revenue', output_field=FloatField()))['total'] or 0
        orders = qs.count()
        return sales, orders

    def get_sales_last_year(start_date, end_date):
        delta = end_date - start_date
        start = start_date.replace(year=last_year)
        end = start + delta
        qs = Order.objects.filter(order_date__gte=start, order_date__lte=end)
        sales = qs.annotate(revenue=F('quantity') * F('product__price')).aggregate(total=Sum('revenue', output_field=FloatField()))['total'] or 0
        return sales

    sales_today, orders_today = get_sales_and_orders(today, today)
    sales_today_last_year = get_sales_last_year(today, today)
    sales_yesterday, orders_yesterday = get_sales_and_orders(yesterday, yesterday)
    sales_yesterday_last_year = get_sales_last_year(yesterday, yesterday)
    sales_last_week, orders_last_week = get_sales_and_orders(start_of_last_week, end_of_last_week)
    sales_last_week_last_year = get_sales_last_year(start_of_last_week, end_of_last_week)
    sales_last_month, orders_last_month = get_sales_and_orders(first_day_last_month, last_day_last_month)
    sales_last_month_last_year = get_sales_last_year(first_day_last_month, last_day_last_month)
    sales_90_days, orders_90_days = get_sales_and_orders(start_90_days_ago, today)
    sales_90_days_last_year = get_sales_last_year(start_90_days_ago, today)

    # Sales this month (revenue)
    sales_this_month = Order.objects.filter(order_date__gte=first_day_this_month).annotate(
        revenue=F('quantity') * F('product__price')
    ).aggregate(total=Sum('revenue', output_field=FloatField()))['total'] or 0
    # Sales last month (revenue)
    sales_last_month = Order.objects.filter(order_date__gte=first_day_last_month, order_date__lte=last_day_last_month).annotate(
        revenue=F('quantity') * F('product__price')
    ).aggregate(total=Sum('revenue', output_field=FloatField()))['total'] or 0
    # % more sales in comparison to last month
    if sales_last_month > 0:
        percent_more_sales = ((sales_this_month - sales_last_month) / sales_last_month) * 100
    else:
        percent_more_sales = 100 if sales_this_month > 0 else 0
    # Revenue per sale this month and last month
    orders_this_month = Order.objects.filter(order_date__gte=first_day_this_month).count()
    orders_last_month = Order.objects.filter(order_date__gte=first_day_last_month, order_date__lte=last_day_last_month).count()
    revenue_per_sale_this_month = sales_this_month / orders_this_month if orders_this_month > 0 else 0
    revenue_per_sale_last_month = sales_last_month / orders_last_month if orders_last_month > 0 else 0
    if revenue_per_sale_last_month > 0:
        percent_revenue_per_sale = ((revenue_per_sale_this_month - revenue_per_sale_last_month) / revenue_per_sale_last_month) * 100
    else:
        percent_revenue_per_sale = 100 if revenue_per_sale_this_month > 0 else 0

    last_month = today - timedelta(days=30)
    recent_orders = Order.objects.filter(order_date__gte=last_month).order_by('-order_date')
    total_item_sales = Order.objects.aggregate(total=Sum('quantity'))['total'] or 0

    # Get sales per day for this month
    sales_per_day_qs = (
        Order.objects.filter(order_date__gte=first_day_this_month, order_date__lte=today)
        .annotate(day=TruncDay('order_date'))
        .values('day')
        .annotate(sales=Sum(F('quantity') * F('product__price'), output_field=FloatField()))
        .order_by('day')
    )
    sales_per_day = [0] * days_in_month
    for entry in sales_per_day_qs:
        day = entry['day'].day
        sales_per_day[day-1] = round(entry['sales'] or 0, 2)

    # Get product sales for this month (sync with OrderItem, not just Order)
    from orders.models import OrderItem
    order_ids = Order.objects.filter(order_date__gte=first_day_this_month).values_list('id', flat=True)
    product_sales_qs = OrderItem.objects.filter(order_id__in=order_ids) \
        .values('product__name') \
        .annotate(total_sold=Sum('quantity')) \
        .order_by('-total_sold')
    product_names = [entry['product__name'] for entry in product_sales_qs]
    sales_counts = [entry['total_sold'] for entry in product_sales_qs]

    context = {
        'total_orders': total_orders,
        'total_item_sales': total_item_sales,
        'total_shipments': total_shipments,
        'total_products': total_products,
        'fulfillment_rate': round(fulfillment_rate, 2),
        'top_products': top_products,
        'top_suppliers': top_suppliers,
        'recent_orders': recent_orders,
        'sales_today': round(sales_today, 2),
        'orders_today': orders_today,
        'sales_today_last_year': round(sales_today_last_year, 2),
        'sales_yesterday': round(sales_yesterday, 2),
        'orders_yesterday': orders_yesterday,
        'sales_yesterday_last_year': round(sales_yesterday_last_year, 2),
        'sales_last_week': round(sales_last_week, 2),
        'orders_last_week': orders_last_week,
        'sales_last_week_last_year': round(sales_last_week_last_year, 2),
        'sales_last_month': round(sales_last_month, 2),
        'orders_last_month': orders_last_month,
        'sales_last_month_last_year': round(sales_last_month_last_year, 2),
        'sales_90_days': round(sales_90_days, 2),
        'orders_90_days': orders_90_days,
        'sales_90_days_last_year': round(sales_90_days_last_year, 2),
        'sales_this_month': round(sales_this_month, 2),
        'percent_more_sales': round(percent_more_sales, 2),
        'percent_revenue_per_sale': round(percent_revenue_per_sale, 2),
        'sales_per_day': sales_per_day,
        'days_in_month': list(range(1, days_in_month+1)),
        'product_names': json.dumps(product_names, cls=DjangoJSONEncoder),
        'sales_counts': json.dumps(sales_counts, cls=DjangoJSONEncoder),
        'notifications': get_notifications(),
    }

    return render(request, 'dashboard-1.html', context)

def notifications(request):
    notifications = []
    # New Orders (last 7 days)
    new_orders = Order.objects.filter(order_date__gte=now().date()-timedelta(days=7)).order_by('-order_date')
    for order in new_orders:
        notifications.append({
            'type': 'order',
            'icon': 'fa-birthday-cake',
            'title': f'New Order #{order.id}',
            'text': f'Order placed by {order.ordered_by.username}',
            'time': order.order_date.strftime('%d %b') if order.order_date else '',
            'timestamp': ensure_aware(order.order_date) if order.order_date else None,
            'order_id': order.id
        })
    # Order Shipments placed (last 7 days)
    new_shipments = Shipment.objects.filter(dispatch_date__gte=now().date()-timedelta(days=7)).order_by('-dispatch_date')
    for shipment in new_shipments:
        notifications.append({
            'type': 'shipment',
            'icon': 'fa-shipping-fast',
            'title': f'Shipment for Order #{shipment.order.id}',
            'text': f'Shipment dispatched: {shipment.tracking_number}',
            'time': shipment.dispatch_date.strftime('%d %b') if shipment.dispatch_date else '',
            'timestamp': ensure_aware(shipment.dispatch_date) if shipment.dispatch_date else now(),
            'order_id': shipment.order.id
        })
    # New Products added (last 7 days)
    new_products = Product.objects.filter().order_by('-id')[:5]
    for product in new_products:
        notifications.append({
            'type': 'product',
            'icon': 'fa-box',
            'title': f'New Product: {product.name}',
            'text': f'Added by {product.created_by.username}',
            'time': product.created_at.strftime('%d %b') if hasattr(product, 'created_at') and product.created_at else '',
            'timestamp': product.created_at if hasattr(product, 'created_at') and product.created_at else now(),
            'order_id': None
        })
    # Inventory low (quantity < 5)
    low_inventory = InventoryItem.objects.filter(quantity__lt=5)
    for item in low_inventory:
        notifications.append({
            'type': 'inventory',
            'icon': 'fa-exclamation-triangle',
            'title': f'Low Inventory: {item.product.name}',
            'text': f'Only {item.quantity} left in stock',
            'time': '',
            'timestamp': now(),
            'order_id': None
        })
    # Invoice paid (last 7 days)
    paid_invoices = Invoice.objects.filter(payment_status='paid', invoice_date__gte=now().date()-timedelta(days=7))
    for invoice in paid_invoices:
        notifications.append({
            'type': 'invoice',
            'icon': 'fa-file-invoice-dollar',
            'title': f'Invoice Paid for Order #{invoice.order.id}',
            'text': f'Invoice #{invoice.invoice_number} paid',
            'time': invoice.invoice_date.strftime('%d %b'),
            'timestamp': ensure_aware(invoice.invoice_date),
            'order_id': invoice.order.id
        })
    # New supplier added (last 7 days)
    new_suppliers = Supplier.objects.filter().order_by('-id')[:5]
    for supplier in new_suppliers:
        notifications.append({
            'type': 'supplier',
            'icon': 'fa-user-plus',
            'title': f'New Supplier: {supplier.name}',
            'text': f'Contact: {supplier.contact_person}',
            'time': '',
            'timestamp': now(),
            'order_id': None
        })
    import datetime as py_datetime
    from django.utils.timezone import is_aware, make_aware, get_current_timezone
    def to_datetime(ts):
        if ts is None:
            ts = now()
        if isinstance(ts, py_datetime.date) and not isinstance(ts, py_datetime.datetime):
            ts = py_datetime.datetime.combine(ts, py_datetime.time.min)
        if not is_aware(ts):
            ts = make_aware(ts, get_current_timezone())
        return ts
    notifications = sorted(
        notifications,
        key=lambda n: to_datetime(n['timestamp']),
        reverse=True
    )
    return render(request, 'notifications.html', {'notifications': notifications})

def analysis(request):
    return render(request, 'dashboard-1.html')
def blank(request):
    context = {
        'notifications': get_notifications(),
    }
    return render(request, 'blank.html', context)

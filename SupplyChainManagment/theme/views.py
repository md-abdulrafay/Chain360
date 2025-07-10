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

    # Calculate percent sales vs yesterday
    if sales_yesterday > 0:
        percent_sales_vs_yesterday = ((sales_today - sales_yesterday) / sales_yesterday) * 100
    else:
        percent_sales_vs_yesterday = 100 if sales_today > 0 else 0

    # Calculate percent orders vs yesterday
    if orders_yesterday > 0:
        percent_orders_vs_yesterday = ((orders_today - orders_yesterday) / orders_yesterday) * 100
    else:
        percent_orders_vs_yesterday = 100 if orders_today > 0 else 0

    # Calculate percent products vs yesterday
    products_yesterday = Product.objects.filter(created_at__date=yesterday).count() if hasattr(Product, 'created_at') else 0
    products_today = Product.objects.filter(created_at__date=today).count() if hasattr(Product, 'created_at') else 0
    if products_yesterday > 0:
        percent_products_vs_yesterday = ((products_today - products_yesterday) / products_yesterday) * 100
    else:
        percent_products_vs_yesterday = 100 if products_today > 0 else 0

    # Calculate percent fulfillment rate vs yesterday
    delivered_shipments_yesterday = Shipment.objects.filter(status='delivered', delivery_date=yesterday).count()
    total_shipments_yesterday = Shipment.objects.filter(delivery_date=yesterday).count()
    if total_shipments_yesterday > 0:
        fulfillment_rate_yesterday = (delivered_shipments_yesterday / total_shipments_yesterday) * 100
    else:
        fulfillment_rate_yesterday = 0
    if fulfillment_rate_yesterday > 0:
        percent_fulfillment_rate_vs_yesterday = ((fulfillment_rate - fulfillment_rate_yesterday) / fulfillment_rate_yesterday) * 100
    else:
        percent_fulfillment_rate_vs_yesterday = 100 if fulfillment_rate > 0 else 0

    last_month = today - timedelta(days=30)
    recent_orders = Order.objects.filter(order_date__gte=last_month).prefetch_related('items__product', 'supplier').order_by('-order_date')
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

    # Get tasks completed by the user this week
    user = request.user
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    completed_orders = Order.objects.filter(ordered_by=user, order_date__gte=start_of_week, order_date__lte=end_of_week, status='delivered')
    completed_shipments = Shipment.objects.filter(order__ordered_by=user, delivery_date__gte=start_of_week, delivery_date__lte=end_of_week, status='delivered')
    completed_products = Product.objects.filter(created_by=user, created_at__date__gte=start_of_week, created_at__date__lte=end_of_week) if hasattr(Product, 'created_by') and hasattr(Product, 'created_at') else []
    tasks_this_week = []
    for order in completed_orders:
        tasks_this_week.append(f"Delivered order #{order.id} for {order.product.name}")
    for shipment in completed_shipments:
        tasks_this_week.append(f"Shipment {shipment.tracking_number} delivered for order #{shipment.order.id}")
    for product in completed_products:
        tasks_this_week.append(f"Added new product: {product.name}")
    # If no tasks, show a default message
    if not tasks_this_week:
        tasks_this_week = ["No tasks completed this week."]
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
        'percent_sales_vs_yesterday': round(percent_sales_vs_yesterday, 2),
        'percent_orders_vs_yesterday': round(percent_orders_vs_yesterday, 2),
        'percent_products_vs_yesterday': round(percent_products_vs_yesterday, 2),
        'percent_fulfillment_rate_vs_yesterday': round(percent_fulfillment_rate_vs_yesterday, 2),
        'sales_per_day': sales_per_day,
        'days_in_month': list(range(1, days_in_month+1)),
        'product_names': json.dumps(product_names, cls=DjangoJSONEncoder),
        'sales_counts': json.dumps(sales_counts, cls=DjangoJSONEncoder),
        'notifications': get_notifications(),
    }
    # Members and online users (use CustomUser from users.models)
    from users.models import CustomUser
    total_members = CustomUser.objects.count()
    online_members = CustomUser.objects.filter(is_active=True).count()  # Adjust logic for 'online' as needed
    context['total_members'] = total_members
    context['online_members'] = online_members
    # Browser stats (example static data, replace with real analytics if available)
    context['browser_stats'] = [
        {'name': 'google chrome', 'icon': 'fab fa-chrome', 'percent': 62},
        {'name': 'firefox', 'icon': 'fab fa-firefox', 'percent': 21},
        {'name': 'internet explorer', 'icon': 'fab fa-internet-explorer', 'percent': 9},
        {'name': 'safari', 'icon': 'fab fa-safari', 'percent': 8},
    ]
    # Fetch recent sales data using OrderItem for accurate product and quantity
    from orders.models import OrderItem
    recent_order_items = OrderItem.objects.select_related('order', 'product').order_by('-order__order_date')[:6]
    context['recent_sales'] = [
        {
            'product': item.product.name,
            'price': item.product.price,
            'quantity': item.quantity,
            'date': item.order.order_date.strftime('%Y-%m-%d') if item.order.order_date else ''
        }
        for item in recent_order_items
    ]
    context['tasks_this_week'] = tasks_this_week
    context['user_name'] = user.get_full_name() or user.username

    # --- Add last 7 days sales and labels for weekly chart ---
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]  # 6 days ago to today
    last_7_days_labels = [d.strftime('%a') for d in last_7_days]  # ['Mon', ...]
    sales_by_date = {d: 0 for d in last_7_days}
    sales_qs = (
        Order.objects.filter(order_date__gte=last_7_days[0], order_date__lte=last_7_days[-1])
        .annotate(day=TruncDay('order_date'))
        .values('day')
        .annotate(sales=Sum(F('quantity') * F('product__price'), output_field=FloatField()))
    )
    for entry in sales_qs:
        day = entry['day'].date() if hasattr(entry['day'], 'date') else entry['day']
        if day in sales_by_date:
            sales_by_date[day] = round(entry['sales'] or 0, 2)
    last_7_days_sales = [sales_by_date[d] for d in last_7_days]
    context['last_7_days_labels'] = json.dumps(last_7_days_labels, cls=DjangoJSONEncoder)
    context['last_7_days_sales'] = json.dumps(last_7_days_sales, cls=DjangoJSONEncoder)

    # Fill dashboard cards with real data
    context['dashboard_sales'] = context.get('sales_this_month', 0)
    context['dashboard_payments'] = Invoice.objects.filter(payment_status='paid', invoice_date__month=today.month, invoice_date__year=today.year).count()
    # Show the real number of orders for this month
    context['dashboard_orders'] = Order.objects.filter(order_date__gte=first_day_this_month, order_date__lte=today).count()
    context['dashboard_items'] = Order.objects.filter(order_date__month=today.month, order_date__year=today.year).aggregate(total=Sum('quantity'))['total'] or 0
    context['dashboard_posts'] = 0  # Replace with real posts count if available
    context['dashboard_posts_active'] = 0  # Replace with real active posts count if available
    context['dashboard_comments'] = 0  # Replace with real comments count if available
    context['dashboard_comments_approved'] = 0  # Replace with real approved comments count if available

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

    # Calculate percent sales vs yesterday
    if sales_yesterday > 0:
        percent_sales_vs_yesterday = ((sales_today - sales_yesterday) / sales_yesterday) * 100
    else:
        percent_sales_vs_yesterday = 100 if sales_today > 0 else 0

    # Calculate percent orders vs yesterday
    if orders_yesterday > 0:
        percent_orders_vs_yesterday = ((orders_today - orders_yesterday) / orders_yesterday) * 100
    else:
        percent_orders_vs_yesterday = 100 if orders_today > 0 else 0

    # Calculate percent products vs yesterday
    products_yesterday = Product.objects.filter(created_at__date=yesterday).count() if hasattr(Product, 'created_at') else 0
    products_today = Product.objects.filter(created_at__date=today).count() if hasattr(Product, 'created_at') else 0
    if products_yesterday > 0:
        percent_products_vs_yesterday = ((products_today - products_yesterday) / products_yesterday) * 100
    else:
        percent_products_vs_yesterday = 100 if products_today > 0 else 0

    # Calculate percent fulfillment rate vs yesterday
    delivered_shipments_yesterday = Shipment.objects.filter(status='delivered', delivery_date=yesterday).count()
    total_shipments_yesterday = Shipment.objects.filter(delivery_date=yesterday).count()
    if total_shipments_yesterday > 0:
        fulfillment_rate_yesterday = (delivered_shipments_yesterday / total_shipments_yesterday) * 100
    else:
        fulfillment_rate_yesterday = 0
    if fulfillment_rate_yesterday > 0:
        percent_fulfillment_rate_vs_yesterday = ((fulfillment_rate - fulfillment_rate_yesterday) / fulfillment_rate_yesterday) * 100
    else:
        percent_fulfillment_rate_vs_yesterday = 100 if fulfillment_rate > 0 else 0

    last_month = today - timedelta(days=30)
    recent_orders = Order.objects.filter(order_date__gte=last_month).prefetch_related('items__product', 'supplier').order_by('-order_date')
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

    # Get tasks completed by the user this week
    user = request.user
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    completed_orders = Order.objects.filter(ordered_by=user, order_date__gte=start_of_week, order_date__lte=end_of_week, status='delivered')
    completed_shipments = Shipment.objects.filter(order__ordered_by=user, delivery_date__gte=start_of_week, delivery_date__lte=end_of_week, status='delivered')
    completed_products = Product.objects.filter(created_by=user, created_at__date__gte=start_of_week, created_at__date__lte=end_of_week) if hasattr(Product, 'created_by') and hasattr(Product, 'created_at') else []
    tasks_this_week = []
    for order in completed_orders:
        tasks_this_week.append(f"Delivered order #{order.id} for {order.product.name}")
    for shipment in completed_shipments:
        tasks_this_week.append(f"Shipment {shipment.tracking_number} delivered for order #{shipment.order.id}")
    for product in completed_products:
        tasks_this_week.append(f"Added new product: {product.name}")
    # If no tasks, show a default message
    if not tasks_this_week:
        tasks_this_week = ["No tasks completed this week."]
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
        'percent_sales_vs_yesterday': round(percent_sales_vs_yesterday, 2),
        'percent_orders_vs_yesterday': round(percent_orders_vs_yesterday, 2),
        'percent_products_vs_yesterday': round(percent_products_vs_yesterday, 2),
        'percent_fulfillment_rate_vs_yesterday': round(percent_fulfillment_rate_vs_yesterday, 2),
        'sales_per_day': sales_per_day,
        'days_in_month': list(range(1, days_in_month+1)),
        'product_names': json.dumps(product_names, cls=DjangoJSONEncoder),
        'sales_counts': json.dumps(sales_counts, cls=DjangoJSONEncoder),
        'notifications': get_notifications(),
    }
    context['tasks_this_week'] = tasks_this_week
    context['user_name'] = user.get_full_name() or user.username

    # --- Add last 7 days sales and labels for weekly chart ---
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]  # 6 days ago to today
    last_7_days_labels = [d.strftime('%a') for d in last_7_days]  # ['Mon', ...]
    sales_by_date = {d: 0 for d in last_7_days}
    sales_qs = (
        Order.objects.filter(order_date__gte=last_7_days[0], order_date__lte=last_7_days[-1])
        .annotate(day=TruncDay('order_date'))
        .values('day')
        .annotate(sales=Sum(F('quantity') * F('product__price'), output_field=FloatField()))
    )
    for entry in sales_qs:
        day = entry['day'].date() if hasattr(entry['day'], 'date') else entry['day']
        if day in sales_by_date:
            sales_by_date[day] = round(entry['sales'] or 0, 2)
    last_7_days_sales = [sales_by_date[d] for d in last_7_days]
    context['last_7_days_labels'] = json.dumps(last_7_days_labels, cls=DjangoJSONEncoder)
    context['last_7_days_sales'] = json.dumps(last_7_days_sales, cls=DjangoJSONEncoder)

    # Fill dashboard cards with real data
    context['dashboard_sales'] = context.get('sales_this_month', 0)
    context['dashboard_payments'] = Invoice.objects.filter(payment_status='paid', invoice_date__month=today.month, invoice_date__year=today.year).count()
    # Show the real number of orders for this month
    context['dashboard_orders'] = Order.objects.filter(order_date__gte=first_day_this_month, order_date__lte=today).count()
    context['dashboard_items'] = Order.objects.filter(order_date__month=today.month, order_date__year=today.year).aggregate(total=Sum('quantity'))['total'] or 0
    context['dashboard_posts'] = 0  # Replace with real posts count if available
    context['dashboard_posts_active'] = 0  # Replace with real active posts count if available
    context['dashboard_comments'] = 0  # Replace with real comments count if available
    context['dashboard_comments_approved'] = 0  # Replace with real approved comments count if available

    # Prepare best sellers data for dashboard-1.html (top 4)
    best_sellers = []
    for entry in product_sales_qs[:4]:
        product = Product.objects.filter(name=entry['product__name']).first()
        price = float(product.price) if product else 0
        total_sold = entry['total_sold']
        total_sales = round(price * total_sold, 2)
        best_sellers.append({
            'name': entry['product__name'],
            'price': price,
            'total_sold': total_sold,
            'total_sales': total_sales,
        })
    context['best_sellers'] = best_sellers
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
    user = request.user
    context = {
        'notifications': get_notifications(),
        'user_name': user.get_full_name() or user.username,
    }
    return render(request, 'blank.html', context)

def sales_details(request):
    today = now().date()
    first_day_this_month = today.replace(day=1)
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    days_in_month = (today.replace(day=calendar.monthrange(today.year, today.month)[1]).day)

    # Sales and orders this month and last month
    sales_this_month = Order.objects.filter(order_date__gte=first_day_this_month).annotate(
        revenue=F('quantity') * F('product__price')
    ).aggregate(total=Sum('revenue', output_field=FloatField()))['total'] or 0
    orders_this_month = Order.objects.filter(order_date__gte=first_day_this_month).count()
    revenue_per_sale_this_month = sales_this_month / orders_this_month if orders_this_month > 0 else 0
    sales_last_month = Order.objects.filter(order_date__gte=first_day_last_month, order_date__lte=last_day_last_month).annotate(
        revenue=F('quantity') * F('product__price')
    ).aggregate(total=Sum('revenue', output_field=FloatField()))['total'] or 0
    orders_last_month = Order.objects.filter(order_date__gte=first_day_last_month, order_date__lte=last_day_last_month).count()
    revenue_per_sale_last_month = sales_last_month / orders_last_month if orders_last_month > 0 else 0

    # Sales per day for this month
    sales_per_day_qs = (
        Order.objects.filter(order_date__gte=first_day_this_month, order_date__lte=today)
        .annotate(day=TruncDay('order_date'))
        .values('day')
        .annotate(sales=Sum(F('quantity') * F('product__price'), output_field=FloatField()))
        .order_by('day')
    )
    sales_per_day_data = [(entry['day'].strftime('%Y-%m-%d'), round(entry['sales'] or 0, 2)) for entry in sales_per_day_qs]

    # Product sales for this month
    order_ids = Order.objects.filter(order_date__gte=first_day_this_month).values_list('id', flat=True)
    product_sales_qs = OrderItem.objects.filter(order_id__in=order_ids) \
        .values('product__name') \
        .annotate(total_sold=Sum('quantity')) \
        .order_by('-total_sold')
    product_sales_data = [(entry['product__name'], entry['total_sold']) for entry in product_sales_qs]

    # Prepare best sellers data for template (top 4)
    best_sellers = []
    for entry in product_sales_qs[:4]:
        product = Product.objects.filter(name=entry['product__name']).first()
        price = float(product.price) if product else 0
        total_sold = entry['total_sold']
        total_sales = round(price * total_sold, 2)
        best_sellers.append({
            'name': entry['product__name'],
            'price': price,
            'total_sold': total_sold,
            'total_sales': total_sales,
        })
    context = {
        'sales_this_month': sales_this_month,
        'orders_this_month': orders_this_month,
        'revenue_per_sale_this_month': revenue_per_sale_this_month,
        'sales_last_month': sales_last_month,
        'orders_last_month': orders_last_month,
        'revenue_per_sale_last_month': revenue_per_sale_last_month,
        'sales_per_day_data': sales_per_day_data,
        'product_sales_data': product_sales_data,
        'best_sellers': best_sellers,
    }
    return render(request, 'sales_details.html', context)

from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    # Dashboard
    path('', views.purchase_dashboard, name='dashboard'),
    path('supplier/', views.supplier_dashboard, name='supplier_dashboard'),
    
    # Purchase Orders
    path('orders/', views.purchase_order_list, name='purchase_order_list'),
    path('orders/create/', views.create_purchase_order, name='create_purchase_order'),
    path('orders/quick/', views.quick_purchase, name='quick_purchase'),
    path('orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('orders/<int:pk>/send/', views.send_to_supplier, name='send_to_supplier'),
    path('orders/<int:pk>/confirm/', views.confirm_purchase_order, name='confirm_purchase_order'),
    path('orders/<int:pk>/receive/', views.receive_goods, name='receive_goods'),
    
    # Invoices
    path('invoices/', views.purchase_invoice_list, name='invoice_list'),
    path('orders/<int:pk>/invoice/', views.create_purchase_invoice, name='create_invoice'),
    path('invoices/<int:pk>/paid/', views.mark_invoice_paid, name='mark_invoice_paid'),
    path('invoices/<int:pk>/download/', views.download_purchase_invoice_pdf, name='download_invoice_pdf'),
    
    # Goods Receipts
    path('receipts/', views.goods_receipt_list, name='receipt_list'),
    path('receipts/<int:pk>/', views.goods_receipt_detail, name='receipt_detail'),
    
    # API endpoints
    path('api/product-price/', views.get_product_price, name='get_product_price'),
]

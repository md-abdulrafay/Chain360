from django.contrib import admin
from .models import PurchaseOrder, PurchaseOrderItem, PurchaseInvoice, GoodsReceipt, GoodsReceiptItem

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'status', 'total_amount', 'created_date']
    list_filter = ['status', 'created_date', 'supplier']
    search_fields = ['po_number', 'supplier__name']
    readonly_fields = ['po_number', 'created_date', 'total_amount']
    inlines = [PurchaseOrderItemInline]

@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'product', 'quantity_ordered', 'quantity_received', 'unit_price', 'total_price']
    list_filter = ['purchase_order__status']

@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'purchase_order', 'invoice_date', 'amount', 'payment_status']
    list_filter = ['payment_status', 'invoice_date']
    search_fields = ['invoice_number', 'purchase_order__po_number']

class GoodsReceiptItemInline(admin.TabularInline):
    model = GoodsReceiptItem
    extra = 1

@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'purchase_order', 'received_date', 'received_by']
    list_filter = ['received_date']
    search_fields = ['receipt_number', 'purchase_order__po_number']
    inlines = [GoodsReceiptItemInline]

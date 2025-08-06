from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_email', 'customer_phone', 'order_date', 'status', 'ordered_by')
    list_filter = ('status', 'order_date', 'ordered_by')
    search_fields = ('customer_name', 'customer_email', 'customer_phone', 'id')
    list_editable = ('status',)
    readonly_fields = ('ordered_by',)
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'customer_address')
        }),
        ('Order Details', {
            'fields': ('product', 'quantity', 'order_date', 'status')
        }),
        ('System Information', {
            'fields': ('ordered_by',),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_selling_price', 'total_price', 'total_profit')
    list_filter = ('order__status', 'product')
    search_fields = ('order__customer_name', 'product__name')


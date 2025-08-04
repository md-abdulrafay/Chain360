from django import forms
from .models import Shipment
from orders.models import Order
from django.db.models import Q

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ['order', 'tracking_number', 'carrier', 'status', 'dispatch_date', 'delivery_date', 'remarks']
        widgets = {
            'order': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'tracking_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'carrier': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'dispatch_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded'}),
            'delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded'}),
            'remarks': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        from shipments.models import Shipment
        shipped_orders = Shipment.objects.values_list('order_id', flat=True)
        
        # Base queryset for orders - only approved orders that haven't been shipped yet
        base_queryset = Order.objects.filter(
            status__in=['approved', 'shipped', 'delivered', 'dispatched']
        )
        
        # Note: No supplier filtering needed since only staff/admin access this form
        
        # If editing, include the current order in the queryset
        instance = kwargs.get('instance', None)
        if instance and instance.order_id:
            self.fields['order'].queryset = base_queryset.filter(
                Q(id=instance.order_id) | ~Q(id__in=shipped_orders)
            )
        else:
            self.fields['order'].queryset = base_queryset.exclude(id__in=shipped_orders)

    def clean(self):
        cleaned_data = super().clean()
        order = cleaned_data.get("order")

        if order and order.status not in ['approved', 'shipped', 'delivered','dispatched']:
            raise forms.ValidationError("You can only create a shipment for orders that are Approved, Shipped, or Delivered.")

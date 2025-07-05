from django import forms
from .models import Shipment
from orders.models import Order

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
        super().__init__(*args, **kwargs)
        # Only show orders with approved, shipped, or delivered status AND no shipment yet
        from shipments.models import Shipment
        shipped_orders = Shipment.objects.values_list('order_id', flat=True)
        self.fields['order'].queryset = Order.objects.filter(
            status__in=['approved', 'shipped', 'delivered']
        ).exclude(id__in=shipped_orders)

    def clean(self):
        cleaned_data = super().clean()
        order = cleaned_data.get("order")

        if order and order.status not in ['approved', 'shipped', 'delivered']:
            raise forms.ValidationError("You can only create a shipment for orders that are Approved, Shipped, or Delivered.")

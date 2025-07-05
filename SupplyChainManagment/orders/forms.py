from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'supplier', 'quantity', 'order_date', 'status']
        widgets = {
            'product': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'supplier': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'order_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
        }

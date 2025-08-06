from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'customer_name', 'customer_email', 'customer_phone', 'customer_address', 'quantity', 'order_date', 'status']
        widgets = {
            'product': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'customer_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded', 'placeholder': 'Enter customer name or leave blank for walk-in customer'}),
            'customer_email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded', 'placeholder': 'Enter customer email'}),
            'customer_phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded', 'placeholder': 'Enter customer phone number'}),
            'customer_address': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded', 'placeholder': 'Enter customer shipping address', 'rows': 3}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'order_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

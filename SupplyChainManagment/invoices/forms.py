from django import forms
from .models import Invoice
from orders.models import Order

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['order', 'invoice_number', 'due_date', 'payment_status']  # Removed 'amount' from fields
        widgets = {
            'order': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'invoice_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded'}),
            'payment_status': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # All users can create invoices for all customer orders
        self.fields['order'].queryset = Order.objects.all()

from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'sku', 'unit_type', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'sku': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'category': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'unit_type': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
        }




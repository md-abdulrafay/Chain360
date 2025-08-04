from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'sku', 'cost_price', 'selling_price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'sku': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'cost_price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded', 'step': '0.01', 'placeholder': 'Purchase price from suppliers'}),
            'selling_price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded', 'step': '0.01', 'placeholder': 'Price charged to customers'}),
            'category': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
        }
        labels = {
            'cost_price': 'Cost Price (Purchase)',
            'selling_price': 'Selling Price (Customer)',
        }
        help_texts = {
            'cost_price': 'The price you pay to suppliers',
            'selling_price': 'The price you charge to customers',
        }




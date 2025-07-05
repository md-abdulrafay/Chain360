from django import forms
from .models import InventoryItem

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['product', 'description', 'quantity', 'unit', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 3}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'unit': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'location': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
        }

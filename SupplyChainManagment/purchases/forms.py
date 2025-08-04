from django import forms
from django.forms import inlineformset_factory
from .models import PurchaseOrder, PurchaseOrderItem, PurchaseInvoice, GoodsReceipt, GoodsReceiptItem
from products.models import Product
from suppliers.models import Supplier

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'expected_delivery_date', 'notes']
        widgets = {
            'expected_delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
        }

class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'quantity_ordered', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity_ordered': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

# Formset for adding multiple items to a purchase order
PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder, 
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=3,
    can_delete=True
)

class PurchaseInvoiceForm(forms.ModelForm):
    class Meta:
        model = PurchaseInvoice
        fields = ['supplier_invoice_number', 'invoice_date', 'due_date', 'amount', 'notes']
        widgets = {
            'supplier_invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class GoodsReceiptForm(forms.ModelForm):
    class Meta:
        model = GoodsReceipt
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class GoodsReceiptItemForm(forms.ModelForm):
    class Meta:
        model = GoodsReceiptItem
        fields = ['quantity_received']
        widgets = {
            'quantity_received': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

# Simple form for quick purchase order creation
class QuickPurchaseForm(forms.Form):
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    unit_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    expected_delivery_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

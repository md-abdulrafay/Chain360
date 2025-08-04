from django import forms
from .models import Supplier
from users.models import CustomUser

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address', 'user']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'contact_person': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'address': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'user': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show users with supplier role who don't already have a supplier record
        used_user_ids = Supplier.objects.exclude(id=self.instance.id if self.instance.pk else None).values_list('user_id', flat=True)
        self.fields['user'].queryset = CustomUser.objects.filter(
            role='supplier'
        ).exclude(id__in=used_user_ids)
        self.fields['user'].empty_label = "Select a supplier user (optional)"

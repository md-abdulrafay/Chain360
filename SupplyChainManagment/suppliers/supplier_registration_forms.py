from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser
from .models import Supplier

class SupplierRegistrationForm(forms.Form):
    # User fields
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'w-full px-3 py-2 border rounded'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'w-full px-3 py-2 border rounded'}))
    
    # Supplier fields
    company_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}))
    contact_person = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded', 'rows': 3}))
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def save(self):
        # Create user
        user = CustomUser.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            role='supplier'
        )
        
        # Create supplier and link to user
        supplier = Supplier.objects.create(
            name=self.cleaned_data['company_name'],
            contact_person=self.cleaned_data['contact_person'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data['phone'],
            address=self.cleaned_data['address'],
            user=user
        )
        
        return user, supplier

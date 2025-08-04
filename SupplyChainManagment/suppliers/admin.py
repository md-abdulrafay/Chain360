from django.contrib import admin
from .models import Supplier

# Register your models here.

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email', 'phone', 'user']
    list_filter = ['user__role']
    search_fields = ['name', 'contact_person', 'email', 'user__username']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


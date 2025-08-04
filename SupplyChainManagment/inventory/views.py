from django.shortcuts import render, redirect, get_object_or_404
from .models import InventoryItem
from .forms import InventoryItemForm
from theme.notification_utils import notify_low_inventory

# Create your views here.

def inventory_list(request):
    items = InventoryItem.objects.all()
    return render(request, 'inventory_list.html', {'items': items})

def add_item(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            
            # Check for low inventory and send notification
            if item.quantity < 5:
                notify_low_inventory(request, item)
            
            return redirect('inventory:inventory_list')
    else:
        form = InventoryItemForm()
    return render(request, 'add_inventory.html', {'form': form})

def edit_item(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            updated_item = form.save()
            
            # Check for low inventory and send notification
            if updated_item.quantity < 5:
                notify_low_inventory(request, updated_item)
            
            return redirect('inventory:inventory_list')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'edit_inventory.html', {'form': form, 'item': item})


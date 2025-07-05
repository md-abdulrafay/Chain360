from django.shortcuts import render, redirect, get_object_or_404
from .models import InventoryItem
from .forms import InventoryItemForm

# Create your views here.

def inventory_list(request):
    items = InventoryItem.objects.all()
    return render(request, 'inventory_list.html', {'items': items})

def add_item(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:inventory_list')
    else:
        form = InventoryItemForm()
    return render(request, 'add_inventory.html', {'form': form})

def edit_item(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('inventory:inventory_list')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'edit_inventory.html', {'form': form, 'item': item})


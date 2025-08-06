from django.db import models
from products.models import Product

# Create your models here.

UNIT_CHOICES = [
    ('piece', 'Piece'),
    ('box', 'Box'),
    ('case', 'Case'),
    ('pallet', 'Pallet'),
    ('kg', 'Kilogram'),
    ('gram', 'Gram'),
    ('liter', 'Liter'),
    ('ml', 'Milliliter'),
    ('meter', 'Meter'),
    ('cm', 'Centimeter'),
    ('pack', 'Pack'),
    ('set', 'Set'),
    ('unit', 'Unit'),
    ('dozen', 'Dozen'),
]

class InventoryItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='piece')
    location = models.CharField(max_length=100, blank=True)
    unit_cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit_selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'unit')  # Prevent duplicate product-unit combinations

    def __str__(self):
        return f"{self.product.name} ({self.quantity} {self.get_unit_display()})"

    @property
    def cost_price(self):
        """Return unit-specific cost price or fallback to product's cost price"""
        return self.unit_cost_price or self.product.cost_price

    @property
    def selling_price(self):
        """Return unit-specific selling price or fallback to product's selling price"""
        return self.unit_selling_price or self.product.selling_price


from django.db import models
from django.conf import settings

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    sku = models.CharField(max_length=50, unique=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Purchase price
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Customer price
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def profit_margin(self):
        """Calculate profit margin per unit"""
        if self.cost_price and self.selling_price:
            return self.selling_price - self.cost_price
        return 0

    @property
    def profit_percentage(self):
        """Calculate profit percentage"""
        if self.cost_price and self.selling_price and self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0


class LedgerEntry(models.Model):
    """
    Profit ledger entry for tracking cost vs selling price for each sale
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_item = models.ForeignKey('orders.OrderItem', on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-calculate profit
        self.profit = (self.selling_price - self.cost_price) * self.quantity_sold
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity_sold} units - Profit: ${self.profit}"

    class Meta:
        ordering = ['-created_at']

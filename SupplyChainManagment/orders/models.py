from django.db import models
from products.models import Product
from django.conf import settings

# Create your models here.

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255, blank=True, null=True, help_text="Customer name for this order")
    quantity = models.PositiveIntegerField()
    order_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    ordered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        if self.order_date:
            return f"Order Id #{self.id} ({self.order_date.strftime('%Y-%m-%d')})"
        else:
            return f"Order Id #{self.id} (No Date)"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Price charged to customer
    unit_cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Cost price from purchases
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Total selling price
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Total profit

    def save(self, *args, **kwargs):
        # Auto-fill prices from product if not set
        if not self.unit_selling_price:
            self.unit_selling_price = self.product.selling_price
        if not self.unit_cost_price:
            self.unit_cost_price = self.product.cost_price
        
        # Calculate totals
        self.total_price = self.quantity * self.unit_selling_price
        self.total_profit = self.quantity * (self.unit_selling_price - self.unit_cost_price)
        
        super().save(*args, **kwargs)
        
        # Create ledger entry for profit tracking
        from products.models import LedgerEntry
        LedgerEntry.objects.update_or_create(
            order_item=self,
            defaults={
                'product': self.product,
                'quantity_sold': self.quantity,
                'cost_price': self.unit_cost_price,
                'selling_price': self.unit_selling_price,
                'profit': self.total_profit
            }
        )

    @property
    def profit_per_unit(self):
        return self.unit_selling_price - self.unit_cost_price

    @property
    def profit_margin_percentage(self):
        if self.unit_cost_price > 0:
            return ((self.unit_selling_price - self.unit_cost_price) / self.unit_cost_price) * 100
        return 0

    def __str__(self):
        return f"{self.quantity} x {self.product.name} - ${self.total_price}"


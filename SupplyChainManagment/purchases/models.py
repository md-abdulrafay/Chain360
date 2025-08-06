from django.db import models
from products.models import Product
from suppliers.models import Supplier
from django.conf import settings
from django.utils import timezone
import uuid

class PurchaseOrder(models.Model):
    """
    Purchase Order - When company wants to buy products from suppliers
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent to Supplier'),
        ('confirmed', 'Confirmed by Supplier'),
        ('partially_received', 'Partially Received'),
        ('received', 'Fully Received'),
        ('cancelled', 'Cancelled'),
    ]

    po_number = models.CharField(max_length=50, unique=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.po_number:
            # Generate PO number: PO-YYYY-XXXX
            year = timezone.now().year
            count = PurchaseOrder.objects.filter(created_date__year=year).count() + 1
            self.po_number = f"PO-{year}-{count:04d}"
        super().save(*args, **kwargs)

    def calculate_total(self):
        """Calculate total amount from all line items"""
        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])
        return total

    def __str__(self):
        return f"{self.po_number} - {self.supplier.name}"

    class Meta:
        ordering = ['-created_date']


class PurchaseOrderItem(models.Model):
    """
    Individual items in a purchase order
    """
    UNIT_TYPE_CHOICES = [
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
    
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_ordered = models.PositiveIntegerField()
    quantity_received = models.PositiveIntegerField(default=0)
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPE_CHOICES, default='piece')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity_ordered * self.unit_price
        super().save(*args, **kwargs)
        # Update PO total
        self.purchase_order.calculate_total()

    @property
    def quantity_pending(self):
        return self.quantity_ordered - self.quantity_received

    @property
    def is_fully_received(self):
        return self.quantity_received >= self.quantity_ordered

    def __str__(self):
        return f"{self.product.name} - {self.quantity_ordered} {self.get_unit_type_display()}"


class PurchaseInvoice(models.Model):
    """
    Invoice from supplier for purchase order
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('overdue', 'Overdue'),
    ]

    invoice_number = models.CharField(max_length=100, unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='invoices')
    supplier_invoice_number = models.CharField(max_length=100, blank=True, help_text="Supplier's invoice number")
    invoice_date = models.DateField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number: PI-YYYY-XXXX
            year = timezone.now().year
            count = PurchaseInvoice.objects.filter(created_date__year=year).count() + 1
            self.invoice_number = f"PI-{year}-{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.purchase_order.supplier.name}"

    class Meta:
        ordering = ['-created_date']


class GoodsReceipt(models.Model):
    """
    Record when goods are actually received from purchase orders
    """
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='receipts')
    received_date = models.DateTimeField(auto_now_add=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate receipt number: GR-YYYY-XXXX
            year = timezone.now().year
            count = GoodsReceipt.objects.filter(received_date__year=year).count() + 1
            self.receipt_number = f"GR-{year}-{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.receipt_number} - {self.purchase_order.po_number}"

    class Meta:
        ordering = ['-received_date']


class GoodsReceiptItem(models.Model):
    """
    Items received in a goods receipt
    """
    goods_receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name='items')
    purchase_order_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.CASCADE)
    quantity_received = models.PositiveIntegerField()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the purchase order item's received quantity
        self.purchase_order_item.quantity_received += self.quantity_received
        self.purchase_order_item.save()
        
        # Update inventory
        from inventory.models import InventoryItem
        try:
            # Look for existing inventory item with same product AND unit type
            inventory_item = InventoryItem.objects.get(
                product=self.purchase_order_item.product,
                unit=self.purchase_order_item.unit_type
            )
            inventory_item.quantity += self.quantity_received
            # Update unit-specific prices if provided in purchase order
            if self.purchase_order_item.unit_price:
                inventory_item.unit_cost_price = self.purchase_order_item.unit_price
            if self.purchase_order_item.unit_selling_price:
                inventory_item.unit_selling_price = self.purchase_order_item.unit_selling_price
            inventory_item.save()
        except InventoryItem.DoesNotExist:
            # Create new inventory item if it doesn't exist, using the same unit type as purchased
            InventoryItem.objects.create(
                product=self.purchase_order_item.product,
                quantity=self.quantity_received,
                unit=self.purchase_order_item.unit_type,  # Use the unit type from purchase order
                unit_cost_price=self.purchase_order_item.unit_price,
                unit_selling_price=self.purchase_order_item.unit_selling_price,
                description=f"Added from Purchase Order {self.goods_receipt.purchase_order.po_number}"
            )

    def __str__(self):
        return f"{self.purchase_order_item.product.name} - {self.quantity_received} units received"

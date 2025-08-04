from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import PurchaseOrder, PurchaseOrderItem, PurchaseInvoice, GoodsReceipt
from products.models import Product, Category
from suppliers.models import Supplier

User = get_user_model()

class PurchaseOrderTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test supplier
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            email='supplier@example.com'
        )
        
        # Create test category and product
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            sku='TEST001',
            price=Decimal('10.00'),
            created_by=self.user
        )
    
    def test_purchase_order_creation(self):
        """Test creating a purchase order"""
        po = PurchaseOrder.objects.create(
            supplier=self.supplier,
            created_by=self.user,
            status='draft'
        )
        
        self.assertEqual(po.supplier, self.supplier)
        self.assertEqual(po.created_by, self.user)
        self.assertEqual(po.status, 'draft')
        self.assertTrue(po.po_number.startswith('PO-'))
    
    def test_purchase_order_item_total_calculation(self):
        """Test that PO item total is calculated correctly"""
        po = PurchaseOrder.objects.create(
            supplier=self.supplier,
            created_by=self.user
        )
        
        item = PurchaseOrderItem.objects.create(
            purchase_order=po,
            product=self.product,
            quantity_ordered=5,
            unit_price=Decimal('12.00')
        )
        
        self.assertEqual(item.total_price, Decimal('60.00'))
    
    def test_purchase_order_total_calculation(self):
        """Test that PO total is calculated from all items"""
        po = PurchaseOrder.objects.create(
            supplier=self.supplier,
            created_by=self.user
        )
        
        # Add multiple items
        PurchaseOrderItem.objects.create(
            purchase_order=po,
            product=self.product,
            quantity_ordered=5,
            unit_price=Decimal('12.00')
        )
        
        # Create another product
        product2 = Product.objects.create(
            name='Test Product 2',
            category=self.category,
            sku='TEST002',
            price=Decimal('15.00'),
            created_by=self.user
        )
        
        PurchaseOrderItem.objects.create(
            purchase_order=po,
            product=product2,
            quantity_ordered=3,
            unit_price=Decimal('15.00')
        )
        
        po.calculate_total()
        self.assertEqual(po.total_amount, Decimal('105.00'))  # 60 + 45

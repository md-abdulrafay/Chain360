#!/usr/bin/env python
"""
Data migration script to move legacy price to cost_price
Run this script to migrate existing price data to the new cost_price field
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SupplyChainManagment.settings')
django.setup()

from products.models import Product

def migrate_price_to_cost_price():
    print("=== Migrating Legacy Price to Cost Price ===")
    
    # Get all products that have a price but no cost_price set
    products_to_migrate = Product.objects.filter(
        cost_price=0.0  # Default value we set
    ).exclude(price=0)
    
    print(f"Found {products_to_migrate.count()} products to migrate")
    
    updated_count = 0
    for product in products_to_migrate:
        old_price = product.price
        product.cost_price = old_price
        # If selling_price is not set, set it to cost_price + 20% markup as default
        if product.selling_price == 0.0:
            product.selling_price = old_price * 1.2  # 20% markup
        product.save()
        
        print(f"✓ {product.name}: price ${old_price} → cost_price ${product.cost_price}, selling_price ${product.selling_price}")
        updated_count += 1
    
    print(f"\n=== Migration Complete ===")
    print(f"Updated {updated_count} products")
    print("Now you can:")
    print("1. Remove the legacy price field from the model")
    print("2. Update forms to not include the legacy price")
    print("3. Update templates to use cost_price instead")

if __name__ == "__main__":
    migrate_price_to_cost_price()

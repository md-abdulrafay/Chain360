# Purchase Management System Documentation

## Overview

I have implemented a complete **Purchase Management System** for your supply chain application. This replaces the manual inventory addition with a proper procurement flow that follows real-world business practices.

## How the Purchase Flow Works

### 1. **Purchase Order Creation (by Admin/Staff)**
- **Who**: Admin or Staff members
- **What**: Create purchase orders to buy products from suppliers
- **Where**: `/purchases/orders/create/` or `/purchases/orders/quick/` for single items
- **Result**: Creates a purchase order in "Draft" status

### 2. **Send to Supplier**
- **Who**: Admin/Staff 
- **What**: Send the purchase order to supplier for confirmation
- **Status Change**: Draft → Sent to Supplier
- **Result**: Supplier gets notified (in real implementation, email would be sent)

### 3. **Supplier Confirmation**
- **Who**: Supplier users (if they have accounts) or Admin on behalf of supplier
- **What**: Supplier confirms they can fulfill the order
- **Status Change**: Sent → Confirmed
- **Result**: Purchase order is ready for delivery

### 4. **Goods Receipt**
- **Who**: Admin/Staff (warehouse team)
- **What**: Record when goods are actually received from supplier
- **Status Change**: Confirmed → Partially Received or Fully Received
- **Result**: **INVENTORY IS AUTOMATICALLY UPDATED** ⭐

### 5. **Purchase Invoice**
- **Who**: Admin/Staff (accounting team)
- **What**: Record the supplier's invoice for payment
- **Result**: Creates financial record for accounts payable

## Key Features Implemented

### ✅ **Automatic Inventory Updates**
- When goods are received, inventory quantities are **automatically increased**
- No more manual inventory entry needed!
- If inventory item doesn't exist, it's created automatically

### ✅ **Multi-User Role Support**
- **Admin/Staff**: Can create purchase orders, receive goods, manage invoices
- **Suppliers**: Can view and confirm their purchase orders (if they have user accounts)

### ✅ **Complete Audit Trail**
- Every purchase order has a unique PO number (PO-2024-0001, etc.)
- Track status changes from draft to received
- Record who created, confirmed, and received each order
- Goods receipt numbers for warehouse tracking

### ✅ **Smart Purchase Orders**
- Support for multiple items per purchase order
- Automatic total calculation
- Partial receipts supported (receive items in multiple shipments)
- Unit price auto-fill from product master data

### ✅ **Financial Integration**
- Purchase invoices linked to purchase orders
- Track payment status (pending, paid, overdue)
- Invoice numbering system

## Files Created

### Models (`purchases/models.py`)
- **PurchaseOrder**: Main purchase order record
- **PurchaseOrderItem**: Individual items in a purchase order
- **PurchaseInvoice**: Supplier invoices
- **GoodsReceipt**: Record of goods received
- **GoodsReceiptItem**: Items received in each receipt

### Views (`purchases/views.py`)
- Dashboard with overview statistics
- Purchase order CRUD operations
- Quick purchase for single items
- Goods receipt processing
- Invoice management

### Templates
- Complete responsive UI using your existing theme
- Dashboard with purchase metrics
- Purchase order forms with dynamic item addition
- Goods receipt forms
- Search and filtering capabilities

## How to Use

### For Admin/Staff (Buying Products):

1. **Go to Purchases Dashboard**: `/purchases/`
2. **Create Quick Purchase**: Click "Quick Purchase" for single items
3. **Or Create Full PO**: Click "New Purchase Order" for multiple items
4. **Send to Supplier**: Once created, click "Send to Supplier"
5. **Confirm Order**: (Supplier does this, or admin can do it)
6. **Receive Goods**: When goods arrive, click "Receive Goods" and enter quantities
7. **Create Invoice**: Record supplier invoice for payment

### For Suppliers (if they have accounts):

1. **View Purchase Orders**: See orders sent to them
2. **Confirm Orders**: Confirm they can fulfill the order
3. **Track Status**: See when goods are received

## Database Changes

The system adds these new tables:
- `purchases_purchaseorder`
- `purchases_purchaseorderitem` 
- `purchases_purchaseinvoice`
- `purchases_goodsreceipt`
- `purchases_goodsreceiptitem`

## Integration with Existing System

### ✅ **Products Integration**
- Uses existing Product model
- Auto-fills unit prices from product data

### ✅ **Suppliers Integration**  
- Uses existing Supplier model
- Supports supplier user accounts

### ✅ **Inventory Integration**
- Automatically updates existing InventoryItem model
- Creates new inventory items if they don't exist

### ✅ **Theme Integration**
- Uses your existing theme/layout
- Added purchase menu to navigation
- Responsive design matching your current UI

## Next Steps

1. **Run the server** and test the purchase flow
2. **Create some test purchase orders**
3. **Receive goods** and see inventory automatically update
4. **Customize** the workflow based on your specific needs

## Benefits vs Manual System

| Manual System | New Purchase System |
|--------------|-------------------|
| ❌ Manual inventory entry | ✅ Automatic inventory updates |
| ❌ No supplier communication | ✅ Formal purchase orders |
| ❌ No audit trail | ✅ Complete tracking |
| ❌ No financial integration | ✅ Invoice management |
| ❌ Error-prone | ✅ Systematic and accurate |

This system follows standard ERP/supply chain practices and gives you a professional procurement workflow!

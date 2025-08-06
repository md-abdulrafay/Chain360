# Chain360 - Supply Chain Management System

<div align="center">
  <img src="SupplyChainManagment/theme/static/img/logo360.png" alt="Chain360 Logo" width="200"/>
  
  [![Django](https://img.shields.io/badge/Django-5.2.3-green.svg)](https://www.djangoproject.com/)
  [![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
  [![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0-38B2AC.svg)](https://tailwindcss.com)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
</div>

## 🚀 Overview

Chain360 is a comprehensive, modern supply chain management system built with Django. It provides end-to-end visibility and control over procurement, inventory management, sales operations, and supplier relationships. The system features a responsive web interface, role-based access control, and real-time analytics.

## ✨ Key Features

### 📊 Dashboard & Analytics
- **Dual Dashboard System**: Analytics dashboard and eCommerce dashboard
- **Real-time Metrics**: Sales trends, inventory levels, profit tracking
- **Interactive Charts**: Visual representation of business data
- **Notification System**: Real-time alerts and task management

### 🛒 Procurement Management
- **Purchase Orders**: Complete PO lifecycle from creation to receipt
- **Quick Purchase**: Single-item rapid procurement
- **Supplier Management**: Comprehensive supplier profiles and relationships
- **Goods Receipt**: Track and confirm deliveries

### 📦 Inventory Management
- **Real-time Stock Tracking**: Monitor inventory levels across locations
- **Multi-unit Support**: Handle various units (pieces, boxes, kg, liters, etc.)
- **Automated Alerts**: Low stock notifications
- **Location-based Tracking**: Warehouse and location management

### 🛍️ Sales & Order Management
- **Order Processing**: Complete order lifecycle management
- **Customer Management**: Track customer relationships and history
- **Invoice Generation**: Automated billing and payment tracking
- **Shipping Integration**: Delivery tracking and carrier management

### 👥 User Management
- **Role-based Access Control**: Different permissions for different user types
- **Custom Authentication**: Secure login and user management
- **Profile Management**: User settings and preferences
- **Team Collaboration**: Multi-user environment support

## 🏗️ System Architecture

### Technology Stack
- **Backend**: Django 5.2.3, Python 3.13
- **Frontend**: TailwindCSS, Font Awesome, JavaScript
- **Database**: SQLite (development), PostgreSQL/MySQL (production ready)
- **Environment**: Conda environment management

### Application Structure
```
SupplyChainManagment/
├── users/              # User management and authentication
├── products/           # Product catalog and profit tracking
├── suppliers/          # Supplier relationship management
├── orders/             # Customer order management
├── inventory/          # Stock tracking and warehouse management
├── shipments/          # Delivery tracking and logistics
├── invoices/           # Customer billing management
├── purchases/          # Procurement and purchase order management
├── profits/            # Profit analysis and reporting
├── theme/              # UI/UX and dashboard components
└── SupplyChainManagment/ # Main project configuration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Conda (recommended) or pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/md-abdulrafay/LogistixPro.git
   cd LogistixPro
   ```

2. **Create and activate conda environment**
   ```bash
   conda env create -f environment.yml
   conda activate supplychain
   ```

3. **Install Python dependencies** (if not using conda)
   ```bash
   pip install django==5.2.3
   pip install django-tailwind
   pip install django-browser-reload
   ```

4. **Navigate to project directory**
   ```bash
   cd SupplyChainManagment
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Install Tailwind CSS dependencies**
   ```bash
   python manage.py tailwind install
   ```

8. **Start development servers**
   ```bash
   # Terminal 1: Django development server
   python manage.py runserver
   
   # Terminal 2: Tailwind CSS watcher (in another terminal)
   python manage.py tailwind start
   ```

9. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000`
   - Login with your superuser credentials

## 📋 Core Modules

### 🛒 Purchases Module
- Purchase Order creation and management
- Quick Purchase functionality
- Supplier selection and management
- Multi-unit type support
- Cost and selling price management
- Goods receipt and confirmation

### 📦 Inventory Module
- Real-time stock level tracking
- Location-based inventory management
- Multi-unit inventory support
- Low stock alerts
- Inventory valuation

### 🛍️ Orders Module
- Customer order processing
- Order status tracking
- Integration with inventory
- Shipping and delivery management

### 🧾 Invoices Module
- Automated invoice generation
- Payment status tracking
- Due date management
- PDF generation and download

### 📊 Analytics Module
- Sales performance tracking
- Profit margin analysis
- Inventory turnover reports
- Supplier performance metrics

## 🎨 User Interface

The system features a modern, responsive design built with TailwindCSS:

- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Dark/Light Theme Support**: User preference-based theming
- **Intuitive Navigation**: Clean sidebar and top navigation
- **Interactive Elements**: Modern buttons, forms, and data tables
- **Real-time Notifications**: Toast notifications for user feedback

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Tailwind Configuration
The project uses django-tailwind for CSS management. Configuration is in `theme/tailwind.config.js`.

## 📚 API Endpoints

### Purchase Orders
- `GET /purchases/` - Purchase dashboard
- `GET /purchases/orders/` - List all purchase orders
- `POST /purchases/orders/create/` - Create new purchase order
- `GET /purchases/orders/quick/` - Quick purchase form
- `GET /purchases/api/product-price/` - Get product pricing

### Inventory
- `GET /inventory/` - Inventory dashboard
- `GET /inventory/list/` - List all inventory items
- `POST /inventory/add/` - Add new inventory item

### Orders
- `GET /orders/` - Order management dashboard
- `GET /orders/list/` - List all orders
- `POST /orders/create/` - Create new order

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test purchases
python manage.py test inventory
```

## 📈 Performance & Scalability

- **Database Optimization**: Efficient queries with select_related and prefetch_related
- **Caching**: Django's caching framework for improved performance
- **Static Files**: Optimized static file serving
- **Database Migration Support**: Easy scaling to PostgreSQL or MySQL

## 🔒 Security Features

- **CSRF Protection**: Built-in Django CSRF protection
- **User Authentication**: Secure login and session management
- **Permission-based Access**: Role-based access control
- **SQL Injection Prevention**: Django ORM protection
- **XSS Protection**: Template auto-escaping

## 🚀 Deployment

### Production Checklist
1. Set `DEBUG = False` in settings
2. Configure proper database (PostgreSQL/MySQL)
3. Set up static file serving
4. Configure email settings
5. Set up monitoring and logging
6. Configure HTTPS
7. Set environment variables

### Docker Deployment (Optional)
```dockerfile
FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **MD Abdul Rafay** - *Initial work* - [md-abdulrafay](https://github.com/md-abdulrafay)

## 🙏 Acknowledgments

- Django community for the excellent framework
- TailwindCSS for the modern UI framework
- Font Awesome for the icon library
- All contributors who have helped shape this project

## 📞 Support

If you have any questions or need help with setup, please:

1. Check the [Issues](https://github.com/md-abdulrafay/LogistixPro/issues) page
2. Create a new issue if your problem isn't already addressed
3. Contact the maintainer: [md-abdulrafay](https://github.com/md-abdulrafay)

## 🗺️ Roadmap

- [ ] Mobile app development
- [ ] Advanced reporting and analytics
- [ ] Multi-warehouse support
- [ ] Integration with external APIs
- [ ] Barcode scanning support
- [ ] Advanced supplier portal
- [ ] AI-powered demand forecasting

---

<div align="center">
  <p>Made with ❤️ by <a href="https://github.com/md-abdulrafay">MD Abdul Rafay</a></p>
</div>

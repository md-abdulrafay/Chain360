from django.urls import path
from .views import dashboard, dashboard_1, notifications, sales_details

urlpatterns = [
    # path('', home, name='home'),
    # path('analysis/', analysis, name='analysis'),
    # path('dashboard/', blank, name='dashboard'),
    path('', dashboard, name='dashboard'),
    path('sales/', dashboard_1, name='dashboard_1'),
    path('notifications/', notifications, name='notifications'),
    path('sales-details/', sales_details, name='sales_details'),
]
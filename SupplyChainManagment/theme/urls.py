from django.urls import path
from .views import dashboard, dashboard_1, notifications, sales_details, test_notifications, clear_messages, role_based_dashboard

urlpatterns = [
    # path('', home, name='home'),
    # path('analysis/', analysis, name='analysis'),
    # path('dashboard/', blank, name='dashboard'),
    path('', role_based_dashboard, name='role_dashboard'),
    path('dashboard/', dashboard, name='dashboard'),
    path('sales/', dashboard_1, name='dashboard_1'),
    path('notifications/', notifications, name='notifications'),
    path('sales-details/', sales_details, name='sales_details'),
    path('test-notifications/', test_notifications, name='test_notifications'),
    path('clear-messages/', clear_messages, name='clear_messages'),
]
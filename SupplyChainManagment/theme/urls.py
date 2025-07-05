from django.urls import path
from .views import dashboard, dashboard_1, notifications

urlpatterns = [
    # path('', home, name='home'),
    # path('analysis/', analysis, name='analysis'),
    # path('dashboard/', blank, name='dashboard'),
    path('', dashboard, name='dashboard'),
    path('sales/', dashboard_1, name='dashboard_1'),
    path('notifications/', notifications, name='notifications'),
]
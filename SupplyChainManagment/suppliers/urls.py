from django.urls import path
from . import views

urlpatterns = [
    path('', views.supplier_list, name='supplier_list'),
    path('add/', views.add_supplier, name='add_supplier'),
    path('register/', views.register_supplier, name='register_supplier'),
    path('dashboard/', views.supplier_dashboard, name='supplier_dashboard'),
    path('edit/<int:pk>/', views.edit_supplier, name='edit_supplier'),
]

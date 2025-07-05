from django.urls import path
from . import views

urlpatterns = [
    path('', views.shipment_list, name='shipment_list'),
    path('add/', views.add_shipment, name='add_shipment'),
    path('edit/<int:pk>/', views.edit_shipment, name='edit_shipment'),
]

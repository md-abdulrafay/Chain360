from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('add/', views.add_item, name='add'),
    path('edit/<int:pk>/', views.edit_item, name='edit'),
]

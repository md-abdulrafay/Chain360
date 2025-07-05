from django.urls import path
from . import views

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('add/', views.add_invoice, name='add_invoice'),
    path('edit/<int:pk>/', views.edit_invoice, name='edit_invoice'),
    path('detail/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('download/<int:pk>/', views.download_invoice_pdf, name='download_invoice_pdf'),
]

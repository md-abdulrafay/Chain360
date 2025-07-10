from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django import forms

# Create your models here.

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('supplier', 'Supplier'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    
    def __str__(self):
        return f"{self.username} ({self.role})"




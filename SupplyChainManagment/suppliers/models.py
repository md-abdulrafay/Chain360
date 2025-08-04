from django.db import models
from django.conf import settings

# Create your models here.

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, 
                               help_text="Link to user account (for supplier role users)")

    def __str__(self):
        return self.name
    
    @classmethod
    def get_for_user(cls, user):
        """Get supplier instance for a given user, returns None if not found"""
        try:
            return cls.objects.get(user=user)
        except cls.DoesNotExist:
            return None

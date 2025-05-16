from django.db import models
from django.contrib.auth.models import User
from gas_stock_management.base.models import BaseModel

class Profile(BaseModel):
     ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Station Manager'),
        ('delivery', 'Delivery Staff'),
        ('customer', 'Customer'),
    ]
     user = models.OneToOneField(User, on_delete=models.CASCADE)
     phone_number = models.CharField(max_length=20, blank=True, null=True)
     address = models.TextField(blank=True, null=True)
     profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
     is_verified = models.BooleanField(default=False)
     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

     def __str__(self):
        return f"{self.user.username} - {self.role}"

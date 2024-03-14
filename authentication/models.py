from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User (AbstractUser):
    profile_pic = models.URLField(max_length=500, blank=True, null=True)
    USER_TYPES = (
        ('customer', 'Customer'),
        ('doctor', 'Doctor')
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='customer')
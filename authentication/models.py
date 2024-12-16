from django.db import models
from django.contrib.auth.models import AbstractUser

class User (AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pictures', default='default_profile_pic.jpg')
    USER_TYPES = (
        ('customer', 'Customer'),
        ('doctor', 'Doctor')
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='customer')
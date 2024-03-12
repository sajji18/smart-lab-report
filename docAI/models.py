from django.db import models
from authentication.models import User

# Create your models here.
class Test (models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    applied_by = models.ForeignKey(User, related_name='customer_tests', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, related_name='doctor_tests', on_delete=models.CASCADE, null=True, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
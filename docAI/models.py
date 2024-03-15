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


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    test = models.ForeignKey(Test, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} to {self.receiver}: {self.content}"

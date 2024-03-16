from django.db import models
from authentication.models import User

# Create your models here.
class Test(models.Model):
    BLOOD_TEST = 'blood'
    DIABETES_TEST = 'diabetes'
    
    TEST_TYPE_CHOICES = [
        (BLOOD_TEST, 'Blood Test'),
        (DIABETES_TEST, 'Diabetes Test'),
    ]
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('submission', 'Submission'),
        ('evaluation', 'Evaluation'),
        ('completed', 'Completed')
    )

    type = models.CharField(max_length=10, choices=TEST_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    applied_by = models.ForeignKey(User, related_name='customer_tests', on_delete=models.CASCADE, null=True, blank=True)
    assigned_to = models.ForeignKey(User, related_name='doctor_tests', on_delete=models.CASCADE)
    
    assigned_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class BloodTestReport(models.Model):
    test = models.OneToOneField(Test, related_name='blood_test_report', on_delete=models.CASCADE)
    
    blood_pressure_result = models.CharField(max_length=20)
    cholesterol_level_result = models.DecimalField(max_digits=5, decimal_places=2)
    

    def __str__(self):
        return f"Blood Test Report for {self.test.name}"


class DiabetesTestReport(models.Model):
    test = models.OneToOneField(Test, related_name='diabetes_test_report', on_delete=models.CASCADE)
    
    blood_sugar_level_result = models.DecimalField(max_digits=5, decimal_places=2)
    insulin_level_result = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Diabetes Test Report for {self.test.name}"


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    test = models.ForeignKey(Test, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} to {self.receiver}: {self.content}"

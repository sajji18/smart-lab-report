from django.db import models
from authentication.models import User
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.
class Test(models.Model):
    BLOOD_TEST = 'blood'
    DIABETES_TEST = 'diabetes'
    
    TEST_TYPE_CHOICES = [
        (BLOOD_TEST, 'Blood Test'),
        (DIABETES_TEST, 'Diabetes Test'),
    ]
    
    type = models.CharField(max_length=10, choices=TEST_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # applicants = models.ManyToManyField(User, through='TestApplication', related_name='customer_tests', blank=True)
    assigned_to = models.ForeignKey(User, related_name='doctor_tests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class TestApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'test')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.test.type == Test.BLOOD_TEST:
            BloodTestReport.objects.get_or_create(test=self.test, applicant=self.user, defaults={'status': 'submission'})
        elif self.test.type == Test.DIABETES_TEST:
            DiabetesTestReport.objects.get_or_create(test=self.test, applicant=self.user, defaults={'status': 'submission'})


class BloodTestReport(models.Model):
    test = models.OneToOneField(Test, related_name='blood_test_report', on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, related_name='blood_test_reports', on_delete=models.CASCADE)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('submission', 'Submission'),
        ('evaluation', 'Evaluation'),
        ('completed', 'Completed')
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending') 
    
    remarks = models.TextField(blank=True)
    
    RBC_result=models.IntegerField(default=0)
    PCV_result=models.IntegerField(default=0)
    WBC_result=models.IntegerField(default=0)
    Neutrophils_result=models.IntegerField(default=0)
    Lymphocytes_result=models.IntegerField(default=0)
    Eosinophils_result=models.IntegerField(default=0)
    Monocytes_result=models.IntegerField(default=0)
    Basophils_result=models.IntegerField(default=0)
    Platelet_count=models.IntegerField(default=0)
    hemoglobin_result=models.IntegerField(default=0)
    blood_pressure_result = models.IntegerField(default=0)
    cholesterol_level_result = models.IntegerField(default=0)
    
    include_applicant_name = models.BooleanField(default=True)
    include_applicant_email = models.BooleanField(default=True)
    include_my_name = models.BooleanField(default=True)
    include_my_email = models.BooleanField(default=True)
    
    include_RBC_Result = models.BooleanField(default=True)
    include_PCV_Result = models.BooleanField(default=True)
    include_WBC_Result = models.BooleanField(default=True)
    include_Neutrophils_Result = models.BooleanField(default=True)
    include_Lymphocytes_Result = models.BooleanField(default=True)
    include_Eosinophils_Result = models.BooleanField(default=True)
    include_Monocytes_Result = models.BooleanField(default=True)
    include_Basophils_Result = models.BooleanField(default=True)
    include_Platelet_Count = models.BooleanField(default=True)
    include_hemoglobin_Result = models.BooleanField(default=True)
    include_blood_pressure_Result = models.BooleanField(default=True)
    include_cholesterol_level_Result = models.BooleanField(default=True)

    def __str__(self):
        return f"Report for {self.test} by {self.applicant}"

    def save(self, *args, **kwargs):
        try:
            TestApplication.objects.get(user=self.applicant, test=self.test)
        except TestApplication.DoesNotExist:
            raise ValueError("The applicant is not associated with this test.")
        super().save(*args, **kwargs)


class DiabetesTestReport(models.Model):
    test = models.OneToOneField(Test, related_name='diabetes_test_report', on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, related_name='diabetes_test_reports', on_delete=models.CASCADE)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('submission', 'Submission'),
        ('evaluation', 'Evaluation'),
        ('completed', 'Completed')
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    remarks = models.TextField(blank=True)
    
    include_applicant_name = models.BooleanField(default=True)
    include_applicant_email = models.BooleanField(default=True)
    include_my_name = models.BooleanField(default=True)
    include_my_email = models.BooleanField(default=True)
    
    blood_sugar_level_result = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    insulin_level_result = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    include_blood_sugar_level_Result = models.BooleanField(default=True)
    include_insulin_level_Result = models.BooleanField(default=True)

    def __str__(self):
        return f"Report for {self.test} by {self.applicant}"

    def save(self, *args, **kwargs):
        try:
            TestApplication.objects.get(user=self.applicant, test=self.test)
        except TestApplication.DoesNotExist:
            raise ValueError("The applicant is not associated with this test.")
        super().save(*args, **kwargs)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    # test = models.ForeignKey(Test, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} to {self.receiver}: {self.content}"
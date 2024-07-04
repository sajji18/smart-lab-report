from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from .models import Test, BloodTestReport, DiabetesTestReport
from django.contrib import admin

class TestAdminForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = '__all__'
        widgets = {
            'applicants': FilteredSelectMultiple('applicants', False)
        }
        
class BloodTestReportForm(forms.ModelForm):
    class Meta:
        model = BloodTestReport
        fields = '__all__'

class DiabetesTestReportForm(forms.ModelForm):
    class Meta:
        model = DiabetesTestReport
        fields = ['blood_sugar_level_result', 'insulin_level_result']
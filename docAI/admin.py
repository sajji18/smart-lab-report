from django.contrib import admin
from .models import Test, Message, BloodTestReport, DiabetesTestReport, TestApplication
from .forms import TestAdminForm

# Register your models here.
@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    form = TestAdminForm
    list_display = ('id', 'assigned_to')
    
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver')
    
admin.site.register(BloodTestReport)
admin.site.register(DiabetesTestReport)
admin.site.register(TestApplication)
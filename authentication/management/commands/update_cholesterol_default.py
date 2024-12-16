from django.core.management.base import BaseCommand
from docAI.models import BloodTestReport

class Command(BaseCommand):
    help = 'Update default value of cholesterol_level_result to 0 for all BloodTestReport instances'
    '''
        Fuction: handle
        Parameters: self, *args, **options
        Return: None
        Description: Updates value of cholesterol_level_result to 0 for all instances of BloodTestReport
    '''
    def handle(self, *args, **options):
        reports = BloodTestReport.objects.all()
        for report in reports:
            report.cholesterol_level_result = 0
            report.save()
        self.stdout.write(self.style.SUCCESS('Default value of cholesterol_level_result set to 0 for all instances of BloodTestReport'))
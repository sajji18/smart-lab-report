from django.core.management.base import BaseCommand
from docAI.models import BloodTestReport

class Command(BaseCommand):
    help = 'Update default value of cholesterol_level_result to 0 for all BloodTestReport instances'

    def handle(self, *args, **options):
        # Get all instances of BloodTestReport
        reports = BloodTestReport.objects.all()

        # Update the default value of cholesterol_level_result
        for report in reports:
            report.cholesterol_level_result = 0
            report.save()

        self.stdout.write(self.style.SUCCESS('Default value of cholesterol_level_result set to 0 for all instances of BloodTestReport'))
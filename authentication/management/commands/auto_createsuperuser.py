from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a superuser with predefined credentials'
    '''
        Fuction: add_arguments
        Parameters: self, parser
        Return: None
        Description: Allows the user to pass in arguments when running the command
    '''
    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the superuser')
        parser.add_argument('--email', type=str, help='Email for the superuser')
        parser.add_argument('--password', type=str, help='Password for the superuser')

    '''
        Fuction: handle
        Parameters: self, *args, **options
        Return: None
        Description: Creates a superuser account with the given credentials
    '''
    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING('Superuser already exists'))
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
from django.core.management.base import BaseCommand
from authentication.models import User

class Command(BaseCommand):
    help = 'Create a user with a hashed password'

    def handle(self, *args, **options):
        username = input('Enter username: ')
        email = input('Enter email address: ')
        password = input('Enter password: ')
        user_type = input('Enter user type: ')

        user = User.objects.create_user(username=username, email=email, password=password, user_type=user_type)
        self.stdout.write(self.style.SUCCESS(f'Successfully created user {user.username}'))

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import getpass


class Command(BaseCommand):
    help = 'Create a superuser interactively'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating superuser...'))
        
        username = input('Username: ')
        email = input('Email address: ')
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User "{username}" already exists.'))
            return
        
        password = getpass.getpass('Password: ')
        password_confirm = getpass.getpass('Password (again): ')
        
        if password != password_confirm:
            self.stdout.write(self.style.ERROR('Passwords do not match.'))
            return
        
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully!'))


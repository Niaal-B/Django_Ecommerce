"""
Django management command to create a superuser with predefined credentials.
Usage: python manage.py create_admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Creates a superuser with username "admin" and password "qwerty"'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@example.com'
        password = 'qwerty'

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists. Skipping creation.')
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created superuser "{username}"')
        )


from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Creates an admin user'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create(
                username='admin',
                email='admin@example.com',
                password=make_password('admin123'),
                is_staff=True,
                is_superuser=True,
                is_active=True,
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('Successfully created admin user'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists')) 
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
django.setup()

from app.user_views.models import User
from django.contrib.auth.hashers import make_password

# Delete existing user if exists
User.objects.filter(email='admin@example.com').delete()

try:
    # Create admin user
    user = User.objects.create(
        email='admin@example.com',
        password=make_password('admin 123'),
        first_name='Admin',
        last_name='User',
        role='admin',
        is_active=True
    )
    print("Admin user created successfully!")
    print("Email: admin@example.com")
    print("Password: admin 123")
except Exception as e:
    print(f"Error creating user: {str(e)}") 
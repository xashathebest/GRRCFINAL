import os
import django
import sys
from datetime import datetime

# Add the current directory to Python path
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_path)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
django.setup()

from app.user_views.models import User
from django.contrib.auth.hashers import make_password

def create_user():
    # Create regular user if it doesn't exist
    user, created = User.objects.get_or_create(
        email='admin@example.com',
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',  # Set role to admin
            'password': make_password('admin123'),
            'is_active': True,
            'date_created': datetime.now().date()
        }
    )
    
    if created:
        print("User created successfully!")
    else:
        print("User already exists.")
    
    print("\nUser setup complete!")
    print("You can now log in with:")
    print("Email: admin@example.com")
    print("Password: admin123")

if __name__ == '__main__':
    create_user() 
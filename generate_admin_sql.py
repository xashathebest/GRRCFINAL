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

from django.contrib.auth.hashers import make_password

def generate_admin_sql():
    password = 'admin123'
    hashed_password = make_password(password)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    sql = f"""INSERT INTO auth_user (
    username,
    password,
    is_superuser,
    first_name,
    last_name,
    email,
    is_staff,
    is_active,
    date_joined
) VALUES (
    'admin',
    '{hashed_password}',
    1,
    'Admin',
    'User',
    'admin@example.com',
    1,
    1,
    '{current_time}'
);"""
    
    print("Run this SQL in your MySQL database:")
    print("\n" + sql)
    print("\nAfter running this SQL, you can log in with:")
    print("Username: admin")
    print("Password: admin123")

if __name__ == '__main__':
    generate_admin_sql() 
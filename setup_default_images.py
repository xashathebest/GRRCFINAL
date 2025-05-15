import os
import django
import sys
from datetime import datetime
from django.core.files import File
from django.conf import settings

# Add the current directory to Python path
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_path)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
django.setup()

from app.user_views.models import MissionVision

def create_default_images():
    # Create default images directory if it doesn't exist
    default_images_dir = os.path.join(settings.MEDIA_ROOT, 'defaults')
    os.makedirs(default_images_dir, exist_ok=True)
    
    # Create a default image if it doesn't exist
    default_image_path = os.path.join(default_images_dir, 'default.jpg')
    if not os.path.exists(default_image_path):
        # Create a simple colored image using PIL
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (1920, 1080), color='#A567E5')  # Purple color matching your theme
        draw = ImageDraw.Draw(img)
        draw.text((960, 540), "Default Background", fill='white')
        img.save(default_image_path)
    
    # Set up MissionVision
    mission_vision, created = MissionVision.objects.get_or_create(id=1)
    if created or not mission_vision.background_image:
        with open(default_image_path, 'rb') as f:
            if not mission_vision.background_image:
                mission_vision.background_image.save('mission_vision/backgrounds/default_background.jpg', File(f), save=False)
            mission_vision.save()
        print("MissionVision images set up successfully!")

if __name__ == '__main__':
    create_default_images() 
from django.db import models # type: ignore
from django.utils import timezone  # type: ignore
from django.core.validators import FileExtensionValidator # type: ignore
from django.core.exceptions import ValidationError # type: ignore

# Create your models here.

# List of Models
#User, Article, ResearchCategry, Research
class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('member', 'Member'),
    ]
    
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    password = models.CharField(max_length=255)  # Hash in production
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'user_views'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="articles/", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        app_label = 'user_views'
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.author}"

class ResearchCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Research(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='research/', null=True, blank=True)
    pdf_file = models.FileField(
        upload_to='research_pdfs/',
        validators=[FileExtensionValidator(['pdf'])],
        null=True,
        blank=True
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    featured_order = models.PositiveSmallIntegerField(default=0)  # For ordering
    category = models.ForeignKey(ResearchCategory, on_delete=models.SET_NULL, null=True, blank=True)



    class Meta:
        app_label = 'user_views'
        verbose_name = 'Research'
        verbose_name_plural = 'Research'
        ordering = ['-is_featured', 'featured_order', '-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        if self.pdf_file and self.pdf_file.size > 10 * 1024 * 1024:  # 10MB limit
            raise ValidationError('PDF file size must not exceed 10MB.')

class FooterInfo(models.Model):
    contact_email = models.EmailField(default="grrc@wmsu.edu.ph")
    contact_phone = models.CharField(max_length=20, default="(+63) 123-4567")
    social_facebook = models.URLField(blank=True, null=True)
    social_instagram = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='footer_logos/', null=True, blank=True)

    def __str__(self):
        return f"Footer Information"
    
    class Meta:
        verbose_name = "Footer Information"
        verbose_name_plural = "Footer Information"

class HeroSection(models.Model):
    title_line_1 = models.CharField(max_length=255)
    title_line_2 = models.CharField(max_length=255)
    description = models.TextField()
    visit_us_link = models.URLField()
    logo_image = models.ImageField(upload_to='hero/')
    background_image = models.ImageField(upload_to='hero/backgrounds/')  # Single responsive image
    learn_more_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title_line_1} {self.title_line_2}"
    

class MissionVision(models.Model):
    mission_title = models.CharField(max_length=255, default="Mission")
    mission_description = models.TextField()
    vision_title = models.CharField(max_length=255, default="Vision")
    vision_description = models.TextField()
    mission_points = models.TextField(blank=True, null=True)
    vision_points = models.TextField(blank=True, null=True)
    background_image = models.ImageField(upload_to='mission_vision/backgrounds/')  # Single responsive image

    def __str__(self):
        return "Mission and Vision Updated"


class KeyObjectives(models.Model):
    heading = models.CharField(max_length=255, default="Key Objectives")
    intro = models.TextField()

    objective_1_title = models.CharField(max_length=255)
    objective_1_text = models.TextField()

    objective_2_title = models.CharField(max_length=255)
    objective_2_text = models.TextField()

    objective_3_title = models.CharField(max_length=255)
    objective_3_text = models.TextField()

    objective_4_title = models.CharField(max_length=255)
    objective_4_text = models.TextField()

    def __str__(self):
        return self.heading
    
class DynamicBannerImage(models.Model):
    image = models.ImageField(upload_to='banner/')  # Single responsive image
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Banner Image {self.id}"
    

class ContentCard(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='cards/')
    order = models.PositiveIntegerField(default=1, help_text="Cards are displayed in ascending order (1, 2, 3...)")

    def __str__(self):
        return self.title
        
    class Meta:
        ordering = ['order', 'id']
    
class TeamMember(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='team_members/')
    linkedin_url = models.URLField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.name


class UGAHeroSection(models.Model):
    heading = models.CharField(max_length=255)
    subheading = models.TextField()
    background_image = models.ImageField(upload_to='hero_images/')

class UGAOverviewSection(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

class UGAOverviewCard(models.Model):
    overview = models.ForeignKey(UGAOverviewSection, on_delete=models.CASCADE)
    icon_class = models.CharField(max_length=100)  # e.g. 'fas fa-balance-scale'
    title = models.CharField(max_length=100)
    description = models.TextField()

class UGAKeyArea(models.Model):
    icon_class = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.TextField()
    link_url = models.URLField(blank=True)

class UGAImplementationStep(models.Model):
    step_number = models.PositiveIntegerField()
    title = models.CharField(max_length=100)
    description = models.TextField()

class UGACallToAction(models.Model):
    heading = models.CharField(max_length=255)
    subheading = models.TextField()
    primary_button = models.CharField(max_length=100)
    primary_url = models.URLField()
    secondary_button = models.CharField(max_length=100)
    secondary_url = models.URLField()

class ThemeSettings(models.Model):
    THEME_CHOICES = [
        ('default', 'Default Brand Theme'),
        ('valentine', 'Valentine\'s Day'),
        ('pride', 'Pride Month'),
        ('custom', 'Custom Theme'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='default')
    is_active = models.BooleanField(default=False)
    
    # Primary Colors
    primary_color = models.CharField(max_length=7, default='#A463E6')  # Main brand color
    secondary_color = models.CharField(max_length=7, default='#924DD8')  # Secondary brand color
    
    # UI Elements
    button_color = models.CharField(max_length=7, default='#A463E6')
    button_hover_color = models.CharField(max_length=7, default='#9F59E6')
    text_color = models.CharField(max_length=7, default='#1F2937')
    background_color = models.CharField(max_length=7, default='#F8FAFC')
    
    # Navigation
    nav_background = models.CharField(max_length=7, default='#A463E6')
    nav_text_color = models.CharField(max_length=7, default='#FFFFFF')
    nav_hover_color = models.CharField(max_length=7, default='#924DD8')
    
    # Status Colors
    success_color = models.CharField(max_length=7, default='#10B981')
    warning_color = models.CharField(max_length=7, default='#F59E0B')
    error_color = models.CharField(max_length=7, default='#EF4444')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate all other themes
            ThemeSettings.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_theme_display()})"

    class Meta:
        verbose_name = "Theme Setting"
        verbose_name_plural = "Theme Settings"

class FooterLink(models.Model):
    LINK_CATEGORIES = (
        ('quick_links', 'Quick Links'),
        ('resources', 'Resources'),
        ('social', 'Social Media')  # Changed from 'other' to match your first definition
    )
    
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=LINK_CATEGORIES, default='quick_links')
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['category', 'order', 'title']
        
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

class Footer(models.Model):
    """Legacy model - use FooterInfo instead"""
    pass

class FooterLink(models.Model):
    LINK_CATEGORIES = (
        ('quick_links', 'Quick Links'),
        ('resources', 'Resources'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=LINK_CATEGORIES, default='other')
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['category', 'order', 'title']
        
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

class CarouselImage(models.Model):
    title = models.CharField(max_length=255, help_text="A title to help identify this image in the admin panel")
    image = models.ImageField(upload_to='carousel/')
    order = models.IntegerField(default=0, help_text="Order in which the image appears in the carousel")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title

class ActivitiesCarousel(models.Model):
    image = models.ImageField(upload_to='activities_carousel/')
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Activities Carousel Image'
        verbose_name_plural = 'Activities Carousel Images'

    def __str__(self):
        return f"Activities Carousel Image - {self.title}"

class AboutUsCarousel(models.Model):
    image = models.ImageField(upload_to='about_us_carousel/')
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'About Us Carousel Image'
        verbose_name_plural = 'About Us Carousel Images'

    def __str__(self):
        return f"About Us Carousel Image - {self.title}"

class UGACarousel(models.Model):
    image = models.ImageField(upload_to='uga_carousel/')
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'UGA Carousel Image'
        verbose_name_plural = 'UGA Carousel Images'

    def __str__(self):
        return f"UGA Carousel Image - {self.title}"

class ResearchCarousel(models.Model):
    image = models.ImageField(upload_to='research_carousel/')
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Research Carousel Image'
        verbose_name_plural = 'Research Carousel Images'

    def __str__(self):
        return f"Research Carousel Image - {self.title}"


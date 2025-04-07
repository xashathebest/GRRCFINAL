from django.db import models # type: ignore
from django.utils import timezone  # type: ignore
from django.core.validators import FileExtensionValidator # type: ignore
from django.core.exceptions import ValidationError # type: ignore

# Create your models here.
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
    date_created = models.DateField(auto_now_add=True)
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
    box1_title = models.CharField(max_length=255)
    box1_content = models.TextField()
    box2_title = models.CharField(max_length=255)
    box2_content = models.TextField()
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

    class Meta:
        app_label = 'user_views'
        verbose_name = 'Research'
        verbose_name_plural = 'Research'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        if self.pdf_file and self.pdf_file.size > 10 * 1024 * 1024:  # 10MB limit
            raise ValidationError('PDF file size must not exceed 10MB.')

     

    

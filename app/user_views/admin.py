from django.contrib import admin # type: ignore
from .models import User, Article

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'role', 'is_active', 'date_created')
    list_filter = ('role', 'is_active')
    search_fields = ('first_name', 'last_name', 'email')
    readonly_fields = ('date_created', 'updated_at')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')

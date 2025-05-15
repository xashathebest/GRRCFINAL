from django.contrib import admin # type: ignore
from .models import User, Article, Footer, FooterLink, CarouselImage, ActivitiesCarousel, FooterInfo

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

@admin.register(FooterLink)
class FooterLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url', 'order')
    list_filter = ('category',)
    search_fields = ('title', 'url')
    list_editable = ('order',)
    ordering = ('category', 'order', 'title')

# Register Footer model
admin.site.register(FooterInfo)

@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
    ordering = ('order', 'created_at')

@admin.register(ActivitiesCarousel)
class ActivitiesCarouselAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle')
    ordering = ('order', '-created_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'image')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    list_per_page = 10
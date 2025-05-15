"""
URL configuration for website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.user_views.urls')),
    # path('cards/', views.card_list, name='card_list'),
    # path('admin/cards/', views.manage_cards, name='manage_cards'),
    # path('admin/cards/create/', views.create_card, name='create_card'),
    # path('admin/cards/<int:card_id>/edit/', views.edit_card, name='edit_card'),
    # path('admin/cards/<int:card_id>/delete/', views.delete_card, name='delete_card'),
]
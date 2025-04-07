from django.urls import path # type: ignore
from . import views
from django.conf import settings # type: ignore
from django.conf.urls.static import static # type: ignore

 
urlpatterns = [
    path('', views.index, name='index'),
    path('admins/', views.home, name='home'),
    path('accounts/', views.account_list, name='account_list'),
    path('article_list/', views.article_list, name='article_list'),
    path('pending_articles/', views.pending_articles, name='pending_articles'),
    path("approve_article/<int:article_id>/", views.approve_article, name="approve_article"),
    path('base/', views.base, name='base'),
    path('login/', views.login_auth, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add_article/', views.add_article, name='add_article'),
    path('edit/<int:article_id>/', views.edit_article, name='edit_article'),
    path('admins/delete_article/<int:article_id>/', views.delete_article, name='delete_article'),
    path('add_user/', views.add_user, name='add_user'),
    path('edit_user/<int:user_id>', views.edit_user, name='edit_user'),
    path("admins/delete_user/<int:user_id>/", views.delete_user, name="delete_user"),
    path('activities/', views.activities, name='activities'),
    path('about_us/', views.about_us, name='about_us'),
    path('uga/', views.uga, name='uga'),
    path('research/', views.research, name='research'),
    path('gender_clubs/', views.gender_clubs, name='gender_clubs'),
    path('approve_research/<int:research_id>/', views.approve_research, name='approve_research'),
    path('edit_research/<int:research_id>/', views.edit_research, name='edit_research'),
    path('delete_research/<int:research_id>/', views.delete_research, name='delete_research'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


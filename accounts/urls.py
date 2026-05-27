from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<int:user_id>/', views.profile_detail, name='profile_detail'),
    path('search/', views.search_users, name='search_users'),
    path('nearby/', views.nearby_users, name='nearby_users'),
]

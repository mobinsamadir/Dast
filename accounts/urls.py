from django.urls import path
from . import views
from .views import RegistrationWizard, FORMS

urlpatterns = [
    path('register/', RegistrationWizard.as_view(FORMS), name='register_wizard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password_reset/confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('profile/', views.my_profile, name='my_profile'),
    path('profile/<int:user_id>/', views.profile_detail, name='profile_detail'),
    path('search/', views.search_users, name='search_users'),
    path('nearby/', views.nearby_users, name='nearby_users'),
]

from django.urls import path
from .views import health_check, growth_dashboard_view

app_name = 'admin_panel'

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('growth/', growth_dashboard_view, name='growth_dashboard'),
]

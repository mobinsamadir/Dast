from django.urls import path
from . import views

urlpatterns = [
    path('status/<uuid:room_id>/', views.call_status_view, name='call_status_api'),
]

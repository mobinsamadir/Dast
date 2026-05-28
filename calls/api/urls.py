from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.CallHistoryView.as_view(), name='api_call_history'),
]

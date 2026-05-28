from django.urls import path
from . import views

urlpatterns = [
    path('active/', views.LotteryListView.as_view(), name='api_lottery_active'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.PlanListView.as_view(), name='api_plans'),
    path('wallet/', views.WalletView.as_view(), name='api_wallet'),
    path('transactions/', views.TransactionListView.as_view(), name='api_transactions'),
    path('spin/', views.DailyGachaSpinView.as_view(), name='daily-spin'),
]

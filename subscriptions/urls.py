from django.urls import path
from . import views

urlpatterns = [
    path('wallet/', views.wallet_view, name='wallet'),
    path('wallet/buy/', views.buy_coins_view, name='buy_coins'),
    path('plans/', views.plans_view, name='plans'),
    path('payment/receipt/', views.upload_receipt_view, name='upload_receipt'),
    path('gifts/', views.gift_catalog_view, name='gift_catalog'),
    path('gifts/send/<int:receiver_id>/', views.send_gift_view, name='send_gift'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.lottery_list_view, name='lottery_list'),
    path('<int:lottery_id>/', views.lottery_detail_view, name='lottery_detail'),
    path('<int:lottery_id>/buy/', views.buy_ticket_view, name='buy_ticket'),
    path('my-tickets/', views.my_tickets_view, name='my_tickets'),
    path('winners/', views.winners_view, name='lottery_winners'),
]

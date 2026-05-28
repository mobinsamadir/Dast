from django.urls import path
from . import views

urlpatterns = [
    path('lobby/', views.LobbyListView.as_view(), name='api_games_lobby'),
]

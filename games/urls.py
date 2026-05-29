from django.urls import path
from . import views

urlpatterns = [
    path('', views.games_lobby_view, name='games_lobby'),
    path('truth-dare/', views.truth_dare_lobby_view, name='truth_dare_lobby'),
    path('truth-dare/room/<uuid:room_id>/', views.truth_dare_room_view, name='truth_dare_room'),
    path('hokm/', views.hokm_lobby_view, name='hokm_lobby'),
    path('hokm/room/<uuid:room_id>/', views.hokm_room_view, name='hokm_room'),
    path('manche/', views.manche_lobby_view, name='manche_lobby'),
    path('manche/room/<uuid:room_id>/', views.manche_room_view, name='manche_room'),
    path('snakes/', views.snakes_lobby_view, name='snakes_lobby'),
    path('snakes/room/<uuid:room_id>/', views.snakes_room_view, name='snakes_room'),
    path('amirza/', views.amirza_lobby_view, name='amirza_lobby'),
    path('amirza/room/<uuid:room_id>/', views.amirza_room_view, name='amirza_room'),
    path('single/', views.single_player_view, name='single_player'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
]

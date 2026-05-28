from django.urls import path
from . import views

urlpatterns = [
    path('rooms/', views.RoomListView.as_view(), name='api_chat_rooms'),
    path('rooms/<uuid:room_id>/messages/', views.MessageHistoryView.as_view(), name='api_chat_messages'),
]

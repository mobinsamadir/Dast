from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_list_view, name='chat_list'),
        path('<uuid:room_id>/', views.chat_room_view, name='chat_room'),
    path('start/<int:user_id>/', views.start_chat_view, name='start_chat'),
    path('report/<int:user_id>/', views.report_user_view, name='report_user'),
    path('group/create/', views.create_group_view, name='create_group'),
    path('channel/create/', views.create_channel_view, name='create_channel'),
    path('group/<uuid:room_id>/settings/', views.group_settings_view, name='group_settings'),
    path('channel/<uuid:room_id>/settings/', views.channel_settings_view, name='channel_settings'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.call_history_view, name='call_history'),
    path('<int:user_id>/', views.initiate_call_view, name='initiate_call'),
    path('room/<uuid:room_id>/', views.call_room_view, name='call_room'),
    path('random/', views.random_call_waiting_view, name='random_call_waiting'),
]

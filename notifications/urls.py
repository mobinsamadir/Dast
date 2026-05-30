from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list_view, name='notifications_list'),
    path('read/<int:notif_id>/', views.mark_as_read_view, name='mark_notif_read'),
    path('read-all/', views.mark_all_as_read_view, name='mark_all_notifs_read'),
]

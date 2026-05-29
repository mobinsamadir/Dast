from django.contrib import admin
from django.urls import path, include
from admin_panel.views import health_check
from backup.views import download_backup
from core.views import landing_page
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', landing_page, name='landing'),
    path('admin/backup/download/', download_backup, name='download_backup'),
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('api/v1/', include('core.api.urls')),
    path('', include('accounts.urls')),
    path('', include('subscriptions.urls')),
    path('chat/', include('chat.urls')),
    path('notifications/', include('notifications.urls')),
    path('calls/', include('calls.urls')),
    path('games/', include('games.urls')),
    path('lottery/', include('lottery.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

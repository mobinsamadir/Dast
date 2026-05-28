from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('accounts/', include('accounts.api.urls')),
    path('chat/', include('chat.api.urls')),
    # Other app endpoints will be included here
]

# Append subscriptions to core/api/urls.py
urlpatterns.append(path('subscriptions/', include('subscriptions.api.urls')))
urlpatterns.append(path('calls/', include('calls.api.urls')))
urlpatterns.append(path('games/', include('games.api.urls')))
urlpatterns.append(path('lottery/', include('lottery.api.urls')))
urlpatterns.append(path('notifications/', include('notifications.api.urls')))
from .views import sync_view
urlpatterns.append(path('sync/', sync_view, name='api_sync'))
urlpatterns.append(path('payments/', include('payments.api.urls')))

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dastdoosti.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from notifications.consumers import NotificationConsumer
from chat.consumers import ChatConsumer
from calls.consumers import WebRTCConsumer
from games.consumers import GameConsumer

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/notifications/", NotificationConsumer.as_asgi()),
            path("ws/chat/<int:room_id>/", ChatConsumer.as_asgi()),
            path("ws/call/<int:room_id>/", WebRTCConsumer.as_asgi()),
            path("ws/game/<uuid:room_id>/", GameConsumer.as_asgi()),
        ])
    ),
})

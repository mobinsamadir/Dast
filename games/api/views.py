from rest_framework import generics, permissions
from .serializers import GameRoomSerializer
from games.models import GameRoom
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

class LobbyListView(generics.ListAPIView):
    serializer_class = GameRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(cache_control(public=True, max_age=60))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return GameRoom.objects.filter(status='WAITING')

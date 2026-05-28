from rest_framework import generics, permissions
from .serializers import ChatRoomSerializer, MessageSerializer
from chat.models import ChatRoom, Message
from rest_framework.pagination import CursorPagination
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

class MessageCursorPagination(CursorPagination):
    page_size = 50
    ordering = '-timestamp'

class RoomListView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(cache_control(public=True, max_age=60))
    def get_queryset(self):
        return self.request.user.chat_rooms.all()

class MessageHistoryView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessageCursorPagination

    @method_decorator(cache_control(public=True, max_age=60))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return Message.objects.filter(room__id=room_id)

    def perform_create(self, serializer):
        room = ChatRoom.objects.get(id=self.kwargs['room_id'])
        serializer.save(sender=self.request.user, room=room)

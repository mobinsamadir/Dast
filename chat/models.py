from django.db import models
from django.conf import settings
import uuid

class ChatRoom(models.Model):
    ROOM_TYPES = (
        ('PRIVATE', 'Private'),
        ('GROUP', 'Group'),
        ('CHANNEL', 'Channel'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='PRIVATE')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name if self.name else f"{self.room_type} Room {self.id}"

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField(null=True, blank=True)
    voice_file = models.FileField(upload_to='chat/voices/', null=True, blank=True)
    image = models.ImageField(upload_to='chat/images/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_flagged = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender}: {self.text[:20]}"

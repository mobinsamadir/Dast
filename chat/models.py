from django.db import models
from django.conf import settings
import uuid
import re

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
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='administered_rooms')

    def __str__(self):
        return self.name if self.name else f"{self.room_type} Room {self.id}"

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    text = models.TextField(null=True, blank=True)
    voice_file = models.FileField(upload_to='chat/voices/', null=True, blank=True)
    image = models.ImageField(upload_to='chat/images/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_flagged = models.BooleanField(default=False)
    is_private_media = models.BooleanField(default=False)
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='read_messages', blank=True)

    def clean_text(self):
        if not self.text:
            return

        # Regex patterns to find phones, links, etc.
        phone_pattern = re.compile(r'(\+98|0)?9\d{9}')
        telegram_pattern = re.compile(r'(t\.me\/|@)[a-zA-Z0-9_]+')
        url_pattern = re.compile(r'(https?:\/\/[^\s]+)')

        cleaned_text = self.text

        # Check if flagged
        if phone_pattern.search(cleaned_text) or telegram_pattern.search(cleaned_text) or url_pattern.search(cleaned_text):
            self.is_flagged = True

        cleaned_text = phone_pattern.sub('***', cleaned_text)
        cleaned_text = telegram_pattern.sub('***', cleaned_text)
        cleaned_text = url_pattern.sub('***', cleaned_text)

        self.text = cleaned_text

    def save(self, *args, **kwargs):
        self.clean_text()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sender}: {self.text[:20] if self.text else 'Media'}"

class UserReport(models.Model):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.TextField(verbose_name='دلیل گزارش')
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report by {self.reporter} against {self.reported_user}"

class Intimacy(models.Model):
    user_one = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='intimacy_one')
    user_two = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='intimacy_two')
    points = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user_one', 'user_two')

    def save(self, *args, **kwargs):
        if self.user_one.id > self.user_two.id:
            self.user_one, self.user_two = self.user_two, self.user_one
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Intimacy({self.user_one.phone_number}, {self.user_two.phone_number}) - {self.points} pts"

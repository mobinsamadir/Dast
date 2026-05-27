from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')

    TYPE_CHOICES = (
        ('Message', 'Message'),
        ('Like', 'Like'),
        ('Subscription', 'Subscription'),
        ('Game', 'Game'),
        ('Call', 'Call'),
        ('System', 'System')
    )
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.phone_number} - {self.notification_type}"

from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')

    TYPE_CHOICES = (
        ('new_message', 'New Message'),
        ('subscription_approved', 'Subscription Approved'),
        ('coin_earned', 'Coin Earned'),
        ('gift_received', 'Gift Received'),
        ('call_incoming', 'Incoming Call'),
        ('lottery_won', 'Lottery Won'),
        ('profile_visited', 'Profile Visited'),
        ('system', 'System')
    )
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='system')
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.phone_number} - {self.notification_type}"

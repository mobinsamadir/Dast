from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{instance.user.id}_notifications",
                {
                    "type": "send_notification",
                    "notification": {
                        "id": instance.id,
                        "message": instance.message,
                        "type": instance.notification_type,
                        "link": instance.link,
                        "created_at": str(instance.created_at)
                    }
                }
            )

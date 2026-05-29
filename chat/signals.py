from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from core.tasks.image_tasks import process_uploaded_image

@receiver(post_save, sender=Message)
def process_message_image(sender, instance, created, **kwargs):
    field_value = instance.image
    if field_value and not str(field_value).endswith('.webp'):
        process_uploaded_image.delay(
            app_label='chat',
            model_name='Message',
            instance_id=instance.pk,
            field_name='image',
            quality=82
        )

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PaymentTransaction
from core.tasks.image_tasks import process_uploaded_image

@receiver(post_save, sender=PaymentTransaction)
def process_receipt_image(sender, instance, created, **kwargs):
    field_value = instance.receipt_image
    if field_value and not str(field_value).endswith('.webp'):
        process_uploaded_image.delay(
            app_label='payments',
            model_name='PaymentTransaction',
            instance_id=instance.pk,
            field_name='receipt_image',
            quality=90
        )

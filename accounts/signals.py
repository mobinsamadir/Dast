from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from core.tasks.image_tasks import process_uploaded_image

@receiver(post_save, sender=CustomUser)
def process_profile_picture(sender, instance, created, **kwargs):
    field_value = instance.profile_picture
    if field_value and not str(field_value).endswith('.webp'):
        process_uploaded_image.delay(
            app_label='accounts',
            model_name='CustomUser',
            instance_id=instance.pk,
            field_name='profile_picture',
            quality=82
        )

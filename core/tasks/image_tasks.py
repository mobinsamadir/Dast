from celery import shared_task
from django.apps import apps
from core.utils.image import process_image
import os
from django.core.files.storage import default_storage

@shared_task
def process_uploaded_image(app_label, model_name, instance_id, field_name, quality=82):
    Model = apps.get_model(app_label, model_name)
    try:
        instance = Model.objects.get(pk=instance_id)
    except Model.DoesNotExist:
        return

    image_field = getattr(instance, field_name)
    if not image_field or not image_field.name:
        return

    original_path = image_field.path
    original_name = image_field.name

    if original_name.endswith('.webp'):
        return

    # Process the image
    webp_image = process_image(image_field, quality=quality)

    if webp_image:
        # Save the new image to the field
        # This will upload the new file
        # We need to use update_fields to avoid triggering signals infinitely
        # if the signal isn't smart enough, but the signal checks for .webp anyway.
        setattr(instance, field_name, webp_image)
        instance.save(update_fields=[field_name])

        # Delete original raw file
        if default_storage.exists(original_name):
            default_storage.delete(original_name)

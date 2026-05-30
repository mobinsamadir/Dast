from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from core.tasks.image_tasks import process_uploaded_image
from subscriptions.models import Wallet
from subscriptions.utils import add_coins

@receiver(post_save, sender=CustomUser)
def process_profile_picture(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
        # Check if they were referred
        if instance.referred_by:
            # Add coins to referrer
            add_coins(instance.referred_by, 50, 'Referral', f"Referral bonus for {instance.phone_number}")
            # Add coins to new user
            add_coins(instance, 20, 'Referral', f"Joined via referral code")

    field_value = instance.profile_picture
    if field_value and not str(field_value).endswith('.webp'):
        process_uploaded_image.delay(
            app_label='accounts',
            model_name='CustomUser',
            instance_id=instance.pk,
            field_name='profile_picture',
            quality=82
        )

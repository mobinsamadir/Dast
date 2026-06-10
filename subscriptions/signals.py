from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import GiftPacket
from core.tasks.image_tasks import process_uploaded_image

@receiver(post_save, sender=GiftPacket)
def process_giftpacket_icon(sender, instance, created, **kwargs):
    field_value = instance.icon
    if field_value and not str(field_value).endswith('.webp'):
        process_uploaded_image.delay(
            app_label='subscriptions',
            model_name='GiftPacket',
            instance_id=instance.pk,
            field_name='icon',
            quality=82
        )

from django.db.models import F
from .models import CoinTransaction

@receiver(post_save, sender=CoinTransaction)
def update_lifetime_coin_burn(sender, instance, created, **kwargs):
    if created and instance.transaction_type in ['Game', 'Purchase', 'Gift']:
        user = instance.wallet.user
        # Increment lifetime_coin_burn efficiently
        user.lifetime_coin_burn = F('lifetime_coin_burn') + instance.amount
        user.save(update_fields=['lifetime_coin_burn'])

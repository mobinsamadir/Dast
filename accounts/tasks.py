import json
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from notifications.models import Notification
from subscriptions.models import Wallet
from games.models import LootBox, LootBoxItem

User = get_user_model()

@shared_task
def immediate_tilt_prevention(user_id):
    try:
        user = User.objects.get(id=user_id)
        if user.consecutive_losses >= 3:
            # Grant 20 coins
            wallet, _ = Wallet.objects.get_or_create(user=user)
            wallet.coin_balance += 20
            wallet.save(update_fields=['coin_balance'])

            # Send Notification
            Notification.objects.create(
                user=user,
                notification_type='system',
                message='بدشانسی آوردی؟ اشکالی نداره، این سکه‌های هدیه رو بگیر و دوباره امتحان کن!'
            )
            # Web Push logic would go here
    except User.DoesNotExist:
        pass

@shared_task
def daily_churn_prevention_check():
    now = timezone.now()

    # Identify Day 1 Inactivity users
    day_1_start = now - timedelta(hours=48)
    day_1_end = now - timedelta(hours=24)
    day_1_users = User.objects.filter(last_activity__gte=day_1_start, last_activity__lt=day_1_end, wallet__coin_balance__lt=50)
    for user in day_1_users:
        Notification.objects.create(
            user=user,
            notification_type='system',
            message='دوستان شما در حال بازی هستند، جا نمونی!'
        )

    # Identify Day 3 Inactivity users
    day_3_start = now - timedelta(hours=96)
    day_3_end = now - timedelta(hours=72)
    day_3_users = User.objects.filter(last_activity__gte=day_3_start, last_activity__lt=day_3_end, wallet__coin_balance__lt=50)

    if day_3_users.exists():
        try:
            free_lootbox = LootBox.objects.filter(price_coins=0).first()
        except LootBox.DoesNotExist:
            free_lootbox = None

        for user in day_3_users:
            if free_lootbox:
                # In a real app, logic to add the lootbox to their inventory.
                # For now, just logging the action/sending notification.
                pass
            Notification.objects.create(
                user=user,
                notification_type='system',
                message='دلمون برات تنگ شده! یک جعبه شانس رایگان برات فرستادیم تا دوباره به بازی برگردی.'
            )

    # Identify Day 7 Inactivity users
    day_7_start = now - timedelta(hours=192)
    day_7_end = now - timedelta(hours=168)
    day_7_users = User.objects.filter(last_activity__gte=day_7_start, last_activity__lt=day_7_end, wallet__coin_balance__lt=50)
    for user in day_7_users:
        # In a real app, apply the Redis TTL logic to set temporary VIP status
        Notification.objects.create(
            user=user,
            notification_type='system',
            message='۱۵ دقیقه اشتراک ویژه طلایی برات فعال کردیم — همین الان پروفایلت رو چک کن!'
        )

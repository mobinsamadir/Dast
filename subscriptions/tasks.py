from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from subscriptions.models import CoinTransaction
from django.db.models import Sum
from datetime import timedelta

@shared_task
def update_whales():
    """
    Calculate the top spenders over the last 30 days and store their IDs in a Redis cache (`whale_ids`).
    """
    thirty_days_ago = timezone.now() - timedelta(days=30)

    # Calculate spending: Gift transactions where amount is negative for the sender
    whale_data = CoinTransaction.objects.filter(
        transaction_type='Gift',
        amount__lt=0,
        created_at__gte=thirty_days_ago
    ).values('wallet__user_id').annotate(
        total_spent=Sum('amount')
    ).order_by('total_spent')[:10]  # Get top 10 (amounts are negative, so order ascending)

    whale_ids = [data['wallet__user_id'] for data in whale_data]
    cache.set('whale_ids', whale_ids, timeout=60 * 60 * 24)  # Cache for 24 hours
    return whale_ids

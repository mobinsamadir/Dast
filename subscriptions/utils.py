from subscriptions.models import Wallet, CoinTransaction
from django.db import transaction
from django.db.models import F
from chat.models import Intimacy

def add_coins(user, amount, transaction_type, description):
    with transaction.atomic():
        wallet, created = Wallet.objects.select_for_update().get_or_create(user=user)
        before = wallet.coin_balance

        # Use F() for mathematical safety
        wallet.coin_balance = F('coin_balance') + amount
        wallet.save(update_fields=['coin_balance'])

        # Refresh from db to get exact new value for logs
        wallet.refresh_from_db()
        after = wallet.coin_balance

        CoinTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            before_balance=before,
            after_balance=after,
            transaction_type=transaction_type,
            description=description
        )
        return True

def deduct_coins(user, amount, transaction_type, description):
    with transaction.atomic():
        wallet, created = Wallet.objects.select_for_update().get_or_create(user=user)
        if wallet.coin_balance >= amount:
            before = wallet.coin_balance

            # Use F() for mathematical safety
            wallet.coin_balance = F('coin_balance') - amount
            wallet.save(update_fields=['coin_balance'])

            # Refresh from db to get exact new value for logs
            wallet.refresh_from_db()
            after = wallet.coin_balance

            CoinTransaction.objects.create(
                wallet=wallet,
                amount=-amount,
                before_balance=before,
                after_balance=after,
                transaction_type=transaction_type,
                description=description
            )
            return True
        return False

def process_gift_transaction(sender, receiver, gift_packet):
    """
    Atomic transaction with Pessimistic Locking to prevent double spending.
    Uses safe integer math for the 15% house edge.
    """
    with transaction.atomic():
        # 1. Lock the sender's wallet
        sender_wallet, _ = Wallet.objects.select_for_update().get_or_create(user=sender)

        if sender_wallet.coin_balance < gift_packet.price:
            return False # Insufficient funds

        # 2. Lock the receiver's wallet
        receiver_wallet, _ = Wallet.objects.select_for_update().get_or_create(user=receiver)

        # 3. Calculate House Edge (using safe integer math to prevent float precision loss)
        # e.g., price = 100, commission = 15.0 => house_edge = int(100 * 150 / 1000) = 15
        commission_scaled = int(gift_packet.admin_commission_percent * 10) # 15.0 -> 150
        house_edge = (gift_packet.price * commission_scaled) // 1000
        receiver_amount = gift_packet.price - house_edge

        sender_before = sender_wallet.coin_balance
        receiver_before = receiver_wallet.coin_balance

        # 4. Deduct using F() expressions for mathematical safety
        sender_wallet.coin_balance = F('coin_balance') - gift_packet.price
        sender_wallet.save(update_fields=['coin_balance'])

        # 5. Add to receiver using F() expression
        receiver_wallet.coin_balance = F('coin_balance') + receiver_amount
        receiver_wallet.save(update_fields=['coin_balance'])

        sender_wallet.refresh_from_db()
        receiver_wallet.refresh_from_db()

        # Log Transactions
        CoinTransaction.objects.create(
            wallet=sender_wallet,
            amount=-gift_packet.price,
            before_balance=sender_before,
            after_balance=sender_wallet.coin_balance,
            transaction_type='Gift',
            description=f"Sent gift '{gift_packet.name}' to {receiver.phone_number}"
        )

        CoinTransaction.objects.create(
            wallet=receiver_wallet,
            amount=receiver_amount,
            before_balance=receiver_before,
            after_balance=receiver_wallet.coin_balance,
            transaction_type='Gift',
            description=f"Received gift '{gift_packet.name}' from {sender.phone_number}"
        )

        # Increment Intimacy
        u1, u2 = (sender, receiver) if sender.id < receiver.id else (receiver, sender)
        intimacy, _ = Intimacy.objects.select_for_update().get_or_create(user_one=u1, user_two=u2)
        intimacy_points = gift_packet.price // 10
        intimacy.points = F('points') + intimacy_points
        intimacy.save(update_fields=['points'])

        # Feature 3: The Whale Crown & Broadcast
        from django.core.cache import cache
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        whale_ids = cache.get('whale_ids', [])
        if sender.id in whale_ids and gift_packet.price > 500:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'global_broadcast',
                {
                    'type': 'broadcast_message',
                    'message': f'👑 [WHALE ALERT] کاربر {sender.phone_number} یک هدیه {gift_packet.price} سکه‌ای ارسال کرد! 👑'
                }
            )

        return True

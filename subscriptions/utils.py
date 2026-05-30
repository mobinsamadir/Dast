from subscriptions.models import Wallet, CoinTransaction
from django.db import transaction

def add_coins(user, amount, transaction_type, description):
    with transaction.atomic():
        wallet, created = Wallet.objects.select_for_update().get_or_create(user=user)
        before = wallet.coin_balance
        wallet.coin_balance += amount
        after = wallet.coin_balance
        wallet.save()

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
            wallet.coin_balance -= amount
            after = wallet.coin_balance
            wallet.save()

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

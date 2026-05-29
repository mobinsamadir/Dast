from subscriptions.models import Wallet, CoinTransaction
from django.db import transaction

def add_coins(user, amount, transaction_type, description):
    with transaction.atomic():
        wallet, created = Wallet.objects.get_or_create(user=user)
        wallet.coin_balance += amount
        wallet.save()

        CoinTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type=transaction_type,
            description=description
        )
        return True

def deduct_coins(user, amount, transaction_type, description):
    with transaction.atomic():
        wallet, created = Wallet.objects.get_or_create(user=user)
        if wallet.coin_balance >= amount:
            wallet.coin_balance -= amount
            wallet.save()

            CoinTransaction.objects.create(
                wallet=wallet,
                amount=-amount,
                transaction_type=transaction_type,
                description=description
            )
            return True
        return False

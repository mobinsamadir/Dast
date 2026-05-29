from django.db import models
from django.conf import settings

class Plan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_days = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return f"{self.name} - {self.duration_days} days"

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.phone_number} - {self.plan.name}"

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    coin_balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.phone_number}'s Wallet ({self.coin_balance} coins)"

class CoinTransaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField()

    TYPE_CHOICES = (
        ('Deposit', 'Deposit'),
        ('Withdrawal', 'Withdrawal'),
        ('Referral', 'Referral'),
        ('Game', 'Game'),
        ('Gift', 'Gift'),
        ('Purchase', 'Purchase')
    )
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class GiftPacket(models.Model):
    icon = models.ImageField(upload_to='subscriptions/icons/', null=True, blank=True)
    name = models.CharField(max_length=100)
    coins = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=0)
    admin_commission_percent = models.FloatField(default=10.0)

    def __str__(self):
        return self.name

class UserGift(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gifts_sent')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gifts_received')
    gift_packet = models.ForeignKey(GiftPacket, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)

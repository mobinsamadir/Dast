from django.db import models
from django.conf import settings
import uuid

class GameRoom(models.Model):
    GAME_CHOICES = (
        ('TRUTH_DARE', 'Truth or Dare'),
        ('HOKM', 'Hokm'),
        ('MANCHE', 'Manche'),
        ('SNAKES', 'Snakes & Ladders'),
        ('AMIRZA', 'Amirza'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game_type = models.CharField(max_length=20, choices=GAME_CHOICES)
    players = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='game_rooms')
    STATUS_CHOICES = (('WAITING', 'Waiting'), ('STARTING', 'Starting'), ('IN_PROGRESS', 'In Progress'), ('FINISHED', 'Finished'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WAITING')
    capacity = models.IntegerField(default=2)
    state = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    entry_fee = models.IntegerField(default=10)
    fast_track_fee = models.IntegerField(default=0, help_text='Fee to skip the queue')
    reward_pool = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.game_type} - {self.id}"

class TruthDareQuestion(models.Model):
    TYPE_CHOICES = (('TRUTH', 'Truth'), ('DARE', 'Dare'))
    q_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    text = models.CharField(max_length=500)

    def __str__(self):
        return f"[{self.q_type}] {self.text[:30]}"

class Gift(models.Model):
    name = models.CharField(max_length=50)
    price_coins = models.IntegerField(default=10)
    animation_url = models.CharField(max_length=200, blank=True, help_text="URL/Path to animation asset")

    def __str__(self):
        return f"{self.name} ({self.price_coins} coins)"

class LootBox(models.Model):
    name = models.CharField(max_length=50)
    price_coins = models.IntegerField(default=0, help_text="0 means free/daily")
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class LootBoxItem(models.Model):
    loot_box = models.ForeignKey(LootBox, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=50)
    weight = models.IntegerField(default=10, help_text="Higher weight = higher chance")
    payout_coins = models.IntegerField(default=0)
    is_jackpot = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} (Weight: {self.weight})"

class BetHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bets')
    room = models.ForeignKey(GameRoom, on_delete=models.SET_NULL, null=True, related_name='bets')
    amount = models.IntegerField()
    target = models.CharField(max_length=100, help_text="Who/What they bet on")
    won = models.BooleanField(default=False)
    payout = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.amount} on {self.target} (Won: {self.won})"

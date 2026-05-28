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
    status = models.CharField(max_length=20, default='WAITING') # WAITING, PLAYING, FINISHED
    created_at = models.DateTimeField(auto_now_add=True)
    entry_fee = models.IntegerField(default=10)
    reward_pool = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.game_type} - {self.id}"

class TruthDareQuestion(models.Model):
    TYPE_CHOICES = (('TRUTH', 'Truth'), ('DARE', 'Dare'))
    q_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    text = models.CharField(max_length=500)

    def __str__(self):
        return f"[{self.q_type}] {self.text[:30]}"

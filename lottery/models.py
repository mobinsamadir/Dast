from django.db import models
from django.conf import settings

class Lottery(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    draw_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    reward_pool = models.IntegerField(default=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Ticket(models.Model):
    lottery = models.ForeignKey(Lottery, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lottery_tickets')
    purchased_at = models.DateTimeField(auto_now_add=True)
    is_winner = models.BooleanField(default=False)

    def __str__(self):
        return f"Ticket for {self.user.display_name} in {self.lottery.name}"

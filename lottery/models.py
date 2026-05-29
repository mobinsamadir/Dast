from django.db import models
from django.conf import settings

class Lottery(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    prize_coins = models.IntegerField(default=1000)
    ticket_price = models.IntegerField(default=50)
    max_tickets_per_user = models.IntegerField(default=5)

    draw_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='lotteries_won')
    winning_ticket = models.ForeignKey('Ticket', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    def __str__(self):
        return f"{self.title} - {self.prize_coins} Coins"

class Ticket(models.Model):
    lottery = models.ForeignKey(Lottery, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lottery_tickets')
    purchase_date = models.DateTimeField(auto_now_add=True)
    ticket_number = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            import uuid
            self.ticket_number = str(uuid.uuid4().hex[:8]).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket {self.ticket_number} for {self.user.phone_number}"

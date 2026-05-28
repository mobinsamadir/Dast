from django.db import models
from django.conf import settings
import uuid

class Call(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    caller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calls_made')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calls_received', null=True, blank=True)
    status = models.CharField(max_length=20, choices=(
        ('WAITING', 'Waiting'),
        ('ACTIVE', 'Active'),
        ('ENDED', 'Ended')
    ), default='WAITING')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    cost_per_minute = models.IntegerField(default=10) # coins per minute

    def __str__(self):
        return f"Call {self.id} - {self.status}"

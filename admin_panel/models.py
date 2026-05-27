from django.db import models

class FeatureFlag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"

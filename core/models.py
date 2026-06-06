from django.db import models

class SiteSettings(models.Model):
    # Singleton Model Pattern
    bank_card_number = models.CharField(max_length=20, default="1234-5678-9012-3456", verbose_name="شماره کارت بانکی")
    telegram_bot_token = models.CharField(max_length=255, blank=True, null=True, verbose_name="توکن ربات تلگرام")

    REPLY_RULE_CHOICES = (
        ('premium_only', 'فقط ویژه (جفت کاربران باید ویژه باشند)'),
        ('sender_premium', 'فرستنده ویژه کافیست (اگر فرستنده ویژه باشد گیرنده هم می‌تواند جواب دهد)'),
    )
    chat_reply_rule = models.CharField(max_length=20, choices=REPLY_RULE_CHOICES, default='sender_premium', verbose_name="قانون جواب دادن به چت")

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return "تنظیمات سایت"

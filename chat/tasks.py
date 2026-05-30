from celery import shared_task
from .models import Message

@shared_task
def scan_old_messages_for_regex_violations():
    messages = Message.objects.filter(is_flagged=False, text__isnull=False)
    updated = 0
    for message in messages:
        old_text = message.text
        message.clean_text()
        if message.is_flagged:
            message.save(update_fields=['text', 'is_flagged'])
            updated += 1
    return f"Scanned messages, flagged {updated} new violations."

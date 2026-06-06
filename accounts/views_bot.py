from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from core.models import SiteSettings
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def bot_verification_view(request):
    user = request.user
    if user.is_bot_verified:
        return redirect('my_profile')

    if not user.bot_verification_token:
        user.bot_verification_token = str(uuid.uuid4())
        user.save()

    site_settings = SiteSettings.load()
    bot_token = site_settings.telegram_bot_token
    # Extract bot username from token or have a separate field, but for now we just show a generic link or assume standard format

    bot_link = f"https://t.me/YourBotUsername?start={user.bot_verification_token}" # Placeholder

    return render(request, 'accounts/bot_verification.html', {'bot_link': bot_link, 'user': user})

@csrf_exempt
def bot_webhook(request):
    # This endpoint is called by the Telegram Bot (or Bale/Rubika) to confirm verification
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')

            # Simple security check - in production you should verify requests come from your bot server
            # e.g., checking a shared secret

            if token:
                user = CustomUser.objects.filter(bot_verification_token=token).first()
                if user:
                    user.is_bot_verified = True
                    user.bot_verification_token = None # single use
                    user.save()
                    return JsonResponse({'status': 'success', 'message': 'User verified'})
            return JsonResponse({'status': 'error', 'message': 'Invalid token'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)

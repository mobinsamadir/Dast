from django.shortcuts import redirect
from django.urls import reverse

class BotVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Paths that should be accessible even if not verified
        path = request.path_info
        allowed_paths = [
            reverse('bot_verification'),
            reverse('bot_webhook'),
            reverse('logout'),
            reverse('landing'),
            reverse('my_profile'),
            '/admin/',
            '/static/',
            '/media/',
        ]

        # Check if the current path is allowed
        is_allowed = False
        for allowed in allowed_paths:
            if path.startswith(allowed):
                is_allowed = True
                break

        # Check for profile picture upload/edit logic on my_profile
        # We allow my_profile so they can upload their photo and edit info

        if not request.user.is_bot_verified and not is_allowed:
            # Only restrict access to Chat, Games, Calls, specific actions
            if path.startswith('/chat/') or path.startswith('/games/') or path.startswith('/calls/') or path.startswith('/subscriptions/'):
                return redirect('bot_verification')

        return self.get_response(request)

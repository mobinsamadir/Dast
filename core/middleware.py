from django.shortcuts import redirect
from django.urls import reverse
from accounts.models import CustomUser

class DeviceBanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        device_ban_cookie = request.COOKIES.get('dd_device_ban')

        # Paths that should be accessible even if banned (e.g. admin or static)
        path = request.path_info
        if path.startswith('/admin/') or path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)

        # If cookie is set, log out user and block
        if device_ban_cookie == 'banned':
            from django.contrib.auth import logout
            if request.user.is_authenticated:
                logout(request)
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("دستگاه شما به دلیل تخلف از قوانین سایت مسدود شده است.")

        # Check if current user is blocked
        if request.user.is_authenticated and getattr(request.user, 'status', '') == 'Blocked':
            from django.contrib.auth import logout
            logout(request)
            response = redirect(reverse('landing'))
            response.set_cookie('dd_device_ban', 'banned', max_age=315360000) # 10 years
            return response

        return self.get_response(request)

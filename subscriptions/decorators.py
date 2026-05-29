from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def subscription_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        has_sub = request.user.subscriptions.filter(is_active=True).exists()
        if not has_sub:
            messages.warning(request, 'برای دسترسی به این بخش باید اشتراک ویژه تهیه کنید.')
            return redirect('plans')

        return view_func(request, *args, **kwargs)
    return _wrapped_view

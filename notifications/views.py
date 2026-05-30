from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.http import JsonResponse

@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    return render(request, 'notifications/list.html', {'notifications': notifications})

@login_required
def mark_as_read_view(request, notif_id):
    try:
        notif = Notification.objects.get(id=notif_id, user=request.user)
        notif.is_read = True
        notif.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        if notif.link:
            return redirect(notif.link)
    except Notification.DoesNotExist:
        pass
    return redirect('notifications_list')

@login_required
def mark_all_as_read_view(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    return redirect('notifications_list')

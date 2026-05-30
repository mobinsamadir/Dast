from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from subscriptions.decorators import subscription_required
from accounts.models import CustomUser
from .models import Call
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import uuid

@login_required
@subscription_required
def call_history_view(request):
    calls = Call.objects.filter(caller=request.user) | Call.objects.filter(receiver=request.user)
    calls = calls.order_by('-start_time')
    return render(request, 'calls/history.html', {'calls': calls})

@login_required
@subscription_required
def initiate_call_view(request, user_id):
    target_user = get_object_or_404(CustomUser, id=user_id)
    if target_user.status == 'Blocked':
        messages.error(request, 'امکان تماس با این کاربر وجود ندارد.')
        return redirect('landing')

    # Check if enough coins for at least 1 min
    if not hasattr(request.user, 'wallet') or request.user.wallet.coin_balance < 20: # Example cost 20
        messages.error(request, 'موجودی سکه شما کافی نیست.')
        return redirect('buy_coins')

    # Create call room
    call = Call.objects.create(caller=request.user, receiver=target_user, cost_per_minute=20)

    # In a real app we would send a notification to the target_user here
    from notifications.models import Notification
    Notification.objects.create(
        user=target_user,
        message=f'تماس دریافتی از {request.user.display_name}',
        notification_type='call_incoming',
        link=f'/calls/room/{call.id}/'
    )

    return redirect('call_room', room_id=call.id)

@login_required
@subscription_required
def call_room_view(request, room_id):
    call = get_object_or_404(Call, id=room_id)
    if request.user != call.caller and request.user != call.receiver:
        messages.error(request, 'شما مجاز به ورود به این تماس نیستید.')
        return redirect('landing')

    return render(request, 'calls/room.html', {'room_id': room_id, 'call': call})

@login_required
@subscription_required
def random_call_waiting_view(request):
    # Check if enough coins
    if not hasattr(request.user, 'wallet') or request.user.wallet.coin_balance < 30: # Example cost 30
        messages.error(request, 'موجودی سکه شما کافی نیست.')
        return redirect('buy_coins')

    # Check daily limit (e.g. 5 calls)
    today = timezone.now().date()
    today_calls = Call.objects.filter(
        caller=request.user,
        start_time__date=today,
        cost_per_minute=30 # distinguish random calls by cost or add a type field
    ).count()

    if today_calls >= 5:
        messages.error(request, 'شما به محدودیت تماس‌های تصادفی روزانه رسیده‌اید.')
        return redirect('landing')

    # Look for a waiting call
    waiting_call = Call.objects.filter(status='WAITING', receiver__isnull=True, cost_per_minute=30).exclude(caller=request.user).first()

    if waiting_call:
        waiting_call.receiver = request.user
        waiting_call.save()
        return redirect('call_room', room_id=waiting_call.id)
    else:
        # Create a new waiting call
        call = Call.objects.create(caller=request.user, cost_per_minute=30)
        return render(request, 'calls/random_waiting.html', {'room_id': call.id})

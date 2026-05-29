from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from subscriptions.decorators import subscription_required
from accounts.models import CustomUser
from .models import Call
from django.contrib import messages
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
    # Basic check if enough coins for at least 1 min
    if getattr(request.user, 'wallet', None) and request.user.wallet.coin_balance < 10:
        messages.error(request, 'موجودی سکه برای برقراری تماس کافی نیست.')
        return redirect('wallet')

    # Create call room
    room_id = uuid.uuid4()
    # In a real app we would send a notification to the target_user here
    return redirect('call_room', room_id=room_id)

@login_required
@subscription_required
def call_room_view(request, room_id):
    # Determine if it's a random call or direct call
    return render(request, 'calls/room.html', {'room_id': room_id})

@login_required
@subscription_required
def random_call_waiting_view(request):
    # In a real app, logic to pair users
    # For now, simulate matching after a few seconds
    room_id = uuid.uuid4()
    return render(request, 'calls/random_waiting.html', {'room_id': room_id})

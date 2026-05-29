from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from subscriptions.decorators import subscription_required
from .models import ChatRoom, Message
from accounts.models import CustomUser
from django.contrib import messages
from subscriptions.utils import deduct_coins

@login_required
@subscription_required
def chat_list_view(request):
    rooms = request.user.chat_rooms.all().order_by('-created_at') # Should ideally order by latest message
    return render(request, 'chat/chat_list.html', {'rooms': rooms})

@login_required
@subscription_required
def chat_room_view(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    if request.user not in room.members.all():
        messages.error(request, 'شما عضو این گفتگو نیستید.')
        return redirect('chat_list')

    messages_list = room.messages.order_by('timestamp')[:50]

    # Simple unread logic could go here

    return render(request, 'chat/chat_room.html', {'room': room, 'messages': messages_list})

@login_required
@subscription_required
def create_group_view(request):
    fee = 100 # Example fee
    if request.method == 'POST':
        name = request.POST.get('name')
        if deduct_coins(request.user, fee, 'Purchase', 'ساخت گروه جدید'):
            room = ChatRoom.objects.create(name=name, room_type='GROUP')
            room.members.add(request.user)
            messages.success(request, 'گروه با موفقیت ساخته شد.')
            return redirect('chat_room', room_id=room.id)
        else:
            messages.error(request, 'موجودی سکه شما کافی نیست.')

    return render(request, 'chat/create_room.html', {'type': 'گروه', 'fee': fee, 'action': 'create_group'})

@login_required
@subscription_required
def create_channel_view(request):
    fee = 200 # Example fee
    if request.method == 'POST':
        name = request.POST.get('name')
        if deduct_coins(request.user, fee, 'Purchase', 'ساخت کانال جدید'):
            room = ChatRoom.objects.create(name=name, room_type='CHANNEL')
            room.members.add(request.user)
            messages.success(request, 'کانال با موفقیت ساخته شد.')
            return redirect('chat_room', room_id=room.id)
        else:
            messages.error(request, 'موجودی سکه شما کافی نیست.')

    return render(request, 'chat/create_room.html', {'type': 'کانال', 'fee': fee, 'action': 'create_channel'})

@login_required
def group_settings_view(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, room_type='GROUP')
    return render(request, 'chat/room_settings.html', {'room': room})

@login_required
def channel_settings_view(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, room_type='CHANNEL')
    return render(request, 'chat/room_settings.html', {'room': room})

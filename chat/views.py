from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message
from subscriptions.decorators import subscription_required
from subscriptions.utils import deduct_coins
from django.contrib import messages
from accounts.models import CustomUser

@login_required
@subscription_required
def chat_list_view(request):
    # Rooms where user is a member or admin
    rooms = request.user.chat_rooms.all() | request.user.administered_rooms.all()
    rooms = rooms.distinct().order_by('-created_at')
    return render(request, 'chat/chat_list.html', {'rooms': rooms})

@login_required
@subscription_required
def chat_room_view(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    if room.room_type in ['GROUP', 'CHANNEL'] and request.user not in room.members.all() and room.admin != request.user:
        messages.error(request, 'شما عضو این اتاق نیستید.')
        return redirect('chat_list')

    messages_list = room.messages.all().order_by('timestamp')[:50]
    return render(request, 'chat/chat_room.html', {'room': room, 'messages': messages_list})

@login_required
@subscription_required
def create_group_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name:
            messages.error(request, 'نام گروه الزامی است.')
            return redirect('create_group')

        cost = 100 # Can make dynamic later
        if deduct_coins(request.user, cost, 'Purchase', 'ساخت گروه'):
            room = ChatRoom.objects.create(name=name, room_type='GROUP', admin=request.user)
            room.members.add(request.user)
            messages.success(request, 'گروه با موفقیت ساخته شد.')
            return redirect('chat_room', room_id=room.id)
        else:
            messages.error(request, 'موجودی سکه برای ساخت گروه کافی نیست.')
            return redirect('buy_coins')
    return render(request, 'chat/create_room.html', {'room_type': 'GROUP', 'cost': 100})

@login_required
@subscription_required
def create_channel_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name:
            messages.error(request, 'نام کانال الزامی است.')
            return redirect('create_channel')

        cost = 200 # Can make dynamic later
        if deduct_coins(request.user, cost, 'Purchase', 'ساخت کانال'):
            room = ChatRoom.objects.create(name=name, room_type='CHANNEL', admin=request.user)
            room.members.add(request.user)
            messages.success(request, 'کانال با موفقیت ساخته شد.')
            return redirect('chat_room', room_id=room.id)
        else:
            messages.error(request, 'موجودی سکه برای ساخت کانال کافی نیست.')
            return redirect('buy_coins')
    return render(request, 'chat/create_room.html', {'room_type': 'CHANNEL', 'cost': 200})

@login_required
@subscription_required
def group_settings_view(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, room_type='GROUP', admin=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_member':
            phone = request.POST.get('phone_number')
            try:
                user = CustomUser.objects.get(phone_number=phone)
                room.members.add(user)
                messages.success(request, 'کاربر افزوده شد.')
            except CustomUser.DoesNotExist:
                messages.error(request, 'کاربر یافت نشد.')
        elif action == 'remove_member':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(CustomUser, id=user_id)
            room.members.remove(user)
            messages.success(request, 'کاربر حذف شد.')
    return render(request, 'chat/room_settings.html', {'room': room})

@login_required
@subscription_required
def channel_settings_view(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, room_type='CHANNEL', admin=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_member':
            phone = request.POST.get('phone_number')
            try:
                user = CustomUser.objects.get(phone_number=phone)
                room.members.add(user)
                messages.success(request, 'کاربر افزوده شد.')
            except CustomUser.DoesNotExist:
                messages.error(request, 'کاربر یافت نشد.')
        elif action == 'remove_member':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(CustomUser, id=user_id)
            room.members.remove(user)
            messages.success(request, 'کاربر حذف شد.')
    return render(request, 'chat/room_settings.html', {'room': room})

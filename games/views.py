from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from subscriptions.decorators import subscription_required
from .models import GameRoom, TruthDareQuestion
from django.contrib import messages
from subscriptions.utils import deduct_coins

@login_required
def games_lobby_view(request):
    has_premium = request.user.subscriptions.filter(is_active=True).exists()
    return render(request, 'games/lobby.html', {'has_premium': has_premium})

def create_or_join_room(request, game_type, template_lobby, view_room_name, entry_fee=10):
    if request.method == 'POST':
        # Create new room
        if deduct_coins(request.user, entry_fee, 'Game', f'ورود به بازی {game_type}'):
            room = GameRoom.objects.create(game_type=game_type, entry_fee=entry_fee, reward_pool=entry_fee)
            room.players.add(request.user)
            return redirect(view_room_name, room_id=room.id)
        else:
            messages.error(request, 'موجودی سکه شما کافی نیست.')
            return redirect('games_lobby')

    # List active rooms for this game
    rooms = GameRoom.objects.filter(game_type=game_type, status='WAITING')
    return render(request, template_lobby, {'rooms': rooms, 'entry_fee': entry_fee})

@login_required
@subscription_required
def truth_dare_lobby_view(request):
    return create_or_join_room(request, 'TRUTH_DARE', 'games/truth_dare_lobby.html', 'truth_dare_room', 10)

@login_required
@subscription_required
def truth_dare_room_view(request, room_id):
    room = get_object_or_404(GameRoom, id=room_id, game_type='TRUTH_DARE')
    if request.user not in room.players.all():
        if room.status == 'WAITING' and deduct_coins(request.user, room.entry_fee, 'Game', 'ورود به بازی'):
            room.players.add(request.user)
            room.reward_pool += room.entry_fee
            room.save()
        else:
            messages.error(request, 'نمی‌توانید وارد این بازی شوید.')
            return redirect('truth_dare_lobby')

    questions = TruthDareQuestion.objects.all()
    return render(request, 'games/truth_dare_room.html', {'room': room, 'questions': questions})

@login_required
@subscription_required
def hokm_lobby_view(request):
    return create_or_join_room(request, 'HOKM', 'games/hokm_lobby.html', 'hokm_room', 50)

@login_required
@subscription_required
def hokm_room_view(request, room_id):
    room = get_object_or_404(GameRoom, id=room_id, game_type='HOKM')
    return render(request, 'games/hokm_room.html', {'room': room})

@login_required
@subscription_required
def manche_lobby_view(request):
    return create_or_join_room(request, 'MANCHE', 'games/manche_lobby.html', 'manche_room', 20)

@login_required
@subscription_required
def manche_room_view(request, room_id):
    room = get_object_or_404(GameRoom, id=room_id, game_type='MANCHE')
    return render(request, 'games/manche_room.html', {'room': room})

@login_required
@subscription_required
def snakes_lobby_view(request):
    return create_or_join_room(request, 'SNAKES', 'games/snakes_lobby.html', 'snakes_room', 15)

@login_required
@subscription_required
def snakes_room_view(request, room_id):
    room = get_object_or_404(GameRoom, id=room_id, game_type='SNAKES')
    return render(request, 'games/snakes_room.html', {'room': room})

@login_required
@subscription_required
def amirza_lobby_view(request):
    return create_or_join_room(request, 'AMIRZA', 'games/amirza_lobby.html', 'amirza_room', 30)

@login_required
@subscription_required
def amirza_room_view(request, room_id):
    room = get_object_or_404(GameRoom, id=room_id, game_type='AMIRZA')
    return render(request, 'games/amirza_room.html', {'room': room})

@login_required
def single_player_view(request):
    if request.method == 'POST':
        # Simple puzzle answer check logic
        answer = request.POST.get('answer', '')
        if answer == 'CorrectAnswer123': # Basic stub
            from subscriptions.utils import add_coins
            add_coins(request.user, 5, 'Game', 'برد در بازی تک‌نفره')
            messages.success(request, 'آفرین! ۵ سکه برنده شدید.')
        else:
            messages.error(request, 'پاسخ اشتباه بود. دوباره تلاش کنید.')
    return render(request, 'games/single_player.html')

@login_required
def leaderboard_view(request):
    from accounts.models import CustomUser
    top_users = CustomUser.objects.filter(status='Active').order_by('-wallet__coin_balance')[:10]
    return render(request, 'games/leaderboard.html', {'top_users': top_users})

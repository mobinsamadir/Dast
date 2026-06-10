from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from .engine import MatchmakingQueue, GameEngine
from .models import GameRoom
import time
import random
import uuid

User = get_user_model()
BOT_INJECTION_DELAY_SECONDS = 30

@shared_task
def evaluate_matchmaking_queues():
    """
    Evaluates the Redis matchmaking queues to form rooms.
    Should be called periodically (e.g., via Celery Beat every 5 seconds).
    """
    # We will implement the skeleton for TRUTH_DARE first
    evaluate_truth_dare_queue()

def inject_bot(gender):
    """
    Finds or creates a bot user of the specified gender.
    """
    bot = User.objects.filter(is_bot_verified=True, gender=gender).first()
    if not bot:
        # Create a fallback bot if none exists
        bot_phone = f"bot_{gender}_{uuid.uuid4().hex[:8]}"
        bot = User.objects.create_user(phone_number=bot_phone, password=uuid.uuid4().hex, is_bot_verified=True, gender=gender, display_name=f"Bot_{gender}")
    return bot

def evaluate_truth_dare_queue():
    queue = MatchmakingQueue('TRUTH_DARE')

    # Get all waiting players
    males = queue.get_waiting_players('مرد', limit=100)
    females = queue.get_waiting_players('زن', limit=100)

    current_time = time.time()

    # Simple pairing (1 male, 1 female)
    while males and females:
        male_data = males.pop(0)
        female_data = females.pop(0)

        male_id = male_data[0].decode('utf-8')
        female_id = female_data[0].decode('utf-8')

        # Remove from queue
        queue.remove_player(male_id, 'مرد')
        queue.remove_player(female_id, 'زن')

        # Create Room
        room = GameRoom.objects.create(
            game_type='TRUTH_DARE',
            status='STARTING',
            capacity=2
        )
        room.players.add(male_id, female_id)

        # Initialize Engine State
        engine = GameEngine(room.id)
        engine.start_game()

    # Bot Injection logic
    # If a player has been waiting > 30s and there's no match
    for male_data in males:
        score = male_data[1]
        actual_join_time = score
        if actual_join_time < current_time - 500: # heuristic for fast-track
            actual_join_time += 1000

        if current_time - actual_join_time > BOT_INJECTION_DELAY_SECONDS:
            male_id = male_data[0].decode('utf-8')
            queue.remove_player(male_id, 'مرد')
            bot = inject_bot('زن')

            room = GameRoom.objects.create(
                game_type='TRUTH_DARE',
                status='STARTING',
                capacity=2
            )
            room.players.add(male_id, bot.id)
            engine = GameEngine(room.id)
            engine.start_game()

    for female_data in females:
        score = female_data[1]
        actual_join_time = score
        if actual_join_time < current_time - 500:
            actual_join_time += 1000

        if current_time - actual_join_time > BOT_INJECTION_DELAY_SECONDS:
            female_id = female_data[0].decode('utf-8')
            queue.remove_player(female_id, 'زن')
            bot = inject_bot('مرد')

            room = GameRoom.objects.create(
                game_type='TRUTH_DARE',
                status='STARTING',
                capacity=2
            )
            room.players.add(female_id, bot.id)
            engine = GameEngine(room.id)
            engine.start_game()

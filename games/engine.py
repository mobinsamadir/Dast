import json
import redis
import time
from decimal import Decimal
from django.conf import settings
from .models import GameRoom

redis_client = redis.Redis.from_url(settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else 'redis://localhost:6379/0')

FAST_TRACK_SCORE = 1000

class MatchmakingQueue:
    def __init__(self, game_type):
        self.game_type = game_type
        self.queue_key_male = f"queue:{game_type}:male"
        self.queue_key_female = f"queue:{game_type}:female"

    def add_player(self, user_id, gender, is_fast_track=False):
        score = time.time()
        if is_fast_track:
            score -= FAST_TRACK_SCORE  # Lower score means higher priority in zrange

        queue_key = self.queue_key_male if gender == 'مرد' else self.queue_key_female
        redis_client.zadd(queue_key, {str(user_id): score})

    def remove_player(self, user_id, gender):
        queue_key = self.queue_key_male if gender == 'مرد' else self.queue_key_female
        redis_client.zrem(queue_key, str(user_id))

    def get_waiting_players(self, gender, limit=1):
        queue_key = self.queue_key_male if gender == 'مرد' else self.queue_key_female
        players = redis_client.zrange(queue_key, 0, limit - 1, withscores=True)
        return players

class GameEngine:
    def __init__(self, room_id):
        self.room_id = room_id
        self.state_key = f"game_state:{room_id}"

    def get_state(self):
        state_data = redis_client.get(self.state_key)
        if state_data:
            state = json.loads(state_data)
            if 'version' not in state:
                state['version'] = 1
            return state

        # Fallback to DB
        try:
            room = GameRoom.objects.get(id=self.room_id)
            state = room.state
            if not isinstance(state, dict):
                state = {}
            if 'version' not in state:
                state['version'] = 1
            return state
        except GameRoom.DoesNotExist:
            return {'version': 1}

    def update_state(self, new_state):
        new_state['version'] = new_state.get('version', 0) + 1
        redis_client.set(self.state_key, json.dumps(new_state))
        # Optional: sync to DB periodically or on game end

    def validate_action(self, action_version):
        state = self.get_state()
        return action_version == state.get('version')

    def start_game(self):
        state = self.get_state()
        state['status'] = 'IN_PROGRESS'
        state['start_time'] = time.time()
        self.update_state(state)

        GameRoom.objects.filter(id=self.room_id).update(status='IN_PROGRESS', state=state)

    def end_game(self, winners):
        from django.db import transaction
        from accounts.models import Wallet

        state = self.get_state()
        state['status'] = 'FINISHED'
        state['winners'] = winners
        state['end_time'] = time.time()
        self.update_state(state)

        # 1. Update GameRoom and handle player payouts
        with transaction.atomic():
            room = GameRoom.objects.select_for_update().get(id=self.room_id)
            room.status = 'FINISHED'
            room.state = state
            room.save()

            # Simple reward logic for players (if any)
            if room.reward_pool > 0 and winners:
                per_winner = room.reward_pool // len(winners)
                for w in winners:
                    try:
                        wallet = Wallet.objects.select_for_update().get(user_id=w)
                        wallet.coin_balance += per_winner
                        wallet.save()
                    except Wallet.DoesNotExist:
                        pass

        # 2. Process Spectator Bets
        self.process_bets(winners)

    def process_bets(self, winners):
        from django.db import transaction
        from accounts.models import Wallet
        from .models import BetHistory

        with transaction.atomic():
            bets = BetHistory.objects.select_for_update().filter(room_id=self.room_id, won=False, payout=0)

            total_pool = sum(b.amount for b in bets)
            if total_pool == 0:
                return

            house_cut = int(total_pool * 0.15)
            net_pool = total_pool - house_cut

            # Identify winning bets based on `target` matching `winners` list
            winning_bets = [b for b in bets if b.target in winners]

            total_winning_stake = sum(b.amount for b in winning_bets)

            if total_winning_stake > 0:
                for b in winning_bets:
                    # Calculate proportional payout with high precision
                    proportion = Decimal(b.amount) / Decimal(total_winning_stake)
                    payout = int(Decimal(net_pool) * proportion)

                    b.won = True
                    b.payout = payout
                    b.save()

                    try:
                        wallet = Wallet.objects.select_for_update().get(user_id=b.user_id)
                        wallet.coin_balance += payout
                        wallet.save()
                    except Wallet.DoesNotExist:
                        pass

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import GameRoom, Gift, BetHistory
from .engine import GameEngine
from accounts.models import Wallet
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'game_{self.room_id}'

        if self.scope['user'].is_anonymous:
            await self.close()
            return

        self.role = await self.determine_role(self.room_id, self.scope['user'])
        if not self.role:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Push initial state
        state = await self.get_game_state(self.room_id)
        await self.send(text_data=json.dumps({
            'type': 'initial_state',
            'state': state,
            'role': self.role
        }))

    async def disconnect(self, close_code):
        if not self.scope['user'].is_anonymous:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'play_turn' and self.role == 'player':
            await self.handle_play_turn(data)
        elif action == 'place_bet' and self.role == 'spectator':
            await self.handle_place_bet(data)
        elif action == 'send_gift':
            await self.handle_send_gift(data)

    async def handle_play_turn(self, data):
        action_version = data.get('version')
        payload = data.get('payload')

        # 1. Validate version to prevent race conditions
        is_valid = await self.validate_state_version(self.room_id, action_version)
        if not is_valid:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'State out of sync. Please wait for the latest state.'
            }))
            return

        # 2. Process turn via Engine
        new_state = await self.process_engine_turn(self.room_id, self.scope['user'].id, payload)

        # 3. Broadcast new state
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_state_update',
                'state': new_state
            }
        )

    async def handle_place_bet(self, data):
        amount = int(data.get('amount', 0))
        target = data.get('target')

        # Check if user is a bot (bots can't bet)
        user = self.scope['user']
        if getattr(user, 'is_bot_verified', False):
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Bots cannot place bets.'}))
            return

        # Hard check: Cannot bet if playing in the room
        is_playing = await self.is_player_in_room(self.room_id, user.id)
        if is_playing:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Cannot place bets on your own game.'}))
            return

        success = await self.process_bet_transaction(self.room_id, self.scope['user'].id, amount, target)

        if success:
            # Broadcast the bet event so UI updates live pools
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'bet_placed',
                    'user': self.scope['user'].display_name,
                    'amount': amount,
                    'target': target
                }
            )
        else:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Insufficient coins for bet.'}))

    async def handle_send_gift(self, data):
        gift_id = data.get('gift_id')
        target_user = data.get('target_user')

        gift_data = await self.process_gift_transaction(self.scope['user'].id, gift_id)
        if gift_data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'gift_sent',
                    'sender': self.scope['user'].display_name,
                    'target': target_user,
                    'gift_animation': gift_data['animation_url'],
                    'gift_name': gift_data['name']
                }
            )
        else:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Cannot send gift.'}))

    # --- Broadcasters ---
    async def game_state_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def bet_placed(self, event):
        await self.send(text_data=json.dumps(event))

    async def gift_sent(self, event):
        await self.send(text_data=json.dumps(event))

    # --- DB/Sync Handlers ---
    @database_sync_to_async
    def determine_role(self, room_id, user):
        try:
            room = GameRoom.objects.get(id=room_id)
            if room.players.filter(id=user.id).exists():
                return 'player'
            return 'spectator'
        except GameRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def get_game_state(self, room_id):
        engine = GameEngine(room_id)
        return engine.get_state()

    @database_sync_to_async
    def validate_state_version(self, room_id, version):
        engine = GameEngine(room_id)
        return engine.validate_action(version)

    @database_sync_to_async
    def process_engine_turn(self, room_id, user_id, payload):
        engine = GameEngine(room_id)
        state = engine.get_state()

        # Example dummy transition logic
        state['last_action_by'] = str(user_id)
        state['payload'] = payload

        engine.update_state(state)
        return state

    @database_sync_to_async
    def process_bet_transaction(self, room_id, user_id, amount, target):
        try:
            with transaction.atomic():
                wallet = Wallet.objects.select_for_update().get(user_id=user_id)
                if wallet.coin_balance >= amount:
                    wallet.coin_balance -= amount
                    wallet.save()
                    room = GameRoom.objects.get(id=room_id)
                    BetHistory.objects.create(user_id=user_id, room=room, amount=amount, target=target)
                    return True
                return False
        except Exception:
            return False

    @database_sync_to_async
    def process_gift_transaction(self, user_id, gift_id):
        try:
            with transaction.atomic():
                gift = Gift.objects.get(id=gift_id)
                wallet = Wallet.objects.select_for_update().get(user_id=user_id)
                if wallet.coin_balance >= gift.price_coins:
                    wallet.coin_balance -= gift.price_coins
                    wallet.save()
                    return {'name': gift.name, 'animation_url': gift.animation_url}
                return None
        except Exception:
            return None

    @database_sync_to_async
    def is_player_in_room(self, room_id, user_id):
        try:
            room = GameRoom.objects.get(id=room_id)
            return room.players.filter(id=user_id).exists()
        except GameRoom.DoesNotExist:
            return False

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import GameRoom

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'game_{self.room_id}'

        if self.scope['user'].is_anonymous:
            await self.close()
            return

        is_valid = await self.check_room(self.room_id, self.scope['user'])
        if not is_valid:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if not self.scope['user'].is_anonymous:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Broadcast game state changes
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_message',
                'data': data,
                'sender': self.scope['user'].display_name
            }
        )

    async def game_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def check_room(self, room_id, user):
        try:
            room = GameRoom.objects.get(id=room_id)
            return room.players.filter(id=user.id).exists()
        except GameRoom.DoesNotExist:
            return False

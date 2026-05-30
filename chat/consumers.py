import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model
from admin_panel.models import FeatureFlag

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        if not self.scope['user'].is_authenticated:
            await self.close()
            return

        has_access = await self.check_room_access()
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if not self.scope['user'].is_authenticated:
            return

        if text_data:
            data = json.loads(text_data)
            action = data.get('action', 'send_message')

            if action == 'send_message':
                # Check feature flags based on room type
                room_type = await self.get_room_type()
                if room_type == 'GROUP':
                    if not await self.is_feature_enabled('groups_enabled'):
                        await self.send(text_data=json.dumps({'error': 'Groups are currently disabled.'}))
                        return
                elif room_type == 'CHANNEL':
                    if not await self.is_feature_enabled('channels_enabled'):
                        await self.send(text_data=json.dumps({'error': 'Channels are currently disabled.'}))
                        return
                    # Only admin can send in channel
                    if not await self.is_room_admin():
                        await self.send(text_data=json.dumps({'error': 'Only admins can post in this channel.'}))
                        return

                text = data.get('text', '')
                reply_to_id = data.get('reply_to', None)
                message = await self.save_message(text, reply_to_id=reply_to_id)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message.text,
                        'sender': self.scope['user'].phone_number,
                        'message_id': str(message.id),
                        'reply_to_id': reply_to_id
                    }
                )
            elif action == 'read_receipt':
                message_id = data.get('message_id')
                await self.mark_as_read(message_id)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_read_receipt',
                        'message_id': message_id,
                        'reader': self.scope['user'].phone_number
                    }
                )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'action': 'new_message',
            'message': event['message'],
            'sender': event['sender'],
            'message_id': event['message_id'],
            'reply_to_id': event.get('reply_to_id')
        }))

    async def chat_read_receipt(self, event):
        await self.send(text_data=json.dumps({
            'action': 'read_receipt',
            'message_id': event['message_id'],
            'reader': event['reader']
        }))

    @database_sync_to_async
    def check_room_access(self):
        try:
            # Check subscription
            if not self.scope['user'].subscriptions.filter(is_active=True).exists():
                return False

            room = ChatRoom.objects.get(id=self.room_id)
            if room.room_type in ['GROUP', 'CHANNEL']:
                return room.members.filter(id=self.scope['user'].id).exists()
            return True # Private rooms check can be more complex, but simplified here
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def get_room_type(self):
        return ChatRoom.objects.get(id=self.room_id).room_type

    @database_sync_to_async
    def is_room_admin(self):
        room = ChatRoom.objects.get(id=self.room_id)
        return room.admin == self.scope['user']

    @database_sync_to_async
    def save_message(self, text, reply_to_id=None):
        room = ChatRoom.objects.get(id=self.room_id)
        reply_msg = None
        if reply_to_id:
            try:
                reply_msg = Message.objects.get(id=reply_to_id)
            except Message.DoesNotExist:
                pass

        msg = Message.objects.create(room=room, sender=self.scope['user'], text=text, reply_to=reply_msg)
        return msg

    @database_sync_to_async
    def mark_as_read(self, message_id):
        try:
            msg = Message.objects.get(id=message_id)
            msg.read_by.add(self.scope['user'])
        except Message.DoesNotExist:
            pass

    @database_sync_to_async
    def is_feature_enabled(self, flag_name):
        try:
            flag = FeatureFlag.objects.get(name=flag_name)
            return flag.is_active
        except FeatureFlag.DoesNotExist:
            return True # default to enabled if not found

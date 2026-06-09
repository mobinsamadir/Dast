import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
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
        await self.channel_layer.group_add(
            'global_broadcast',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            'global_broadcast',
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if not self.scope['user'].is_authenticated:
            return

        # Distributed Rate Limiting (Redis-backed via Django Cache)
        # Limit: 3 actions per second per user globally
        user_id = self.scope['user'].id
        cache_key = f"ws_ratelimit_{user_id}"

        # We use a simple counter with a 1-second expiration
        current_count = cache.get(cache_key, 0)
        if current_count >= 3:
            await self.send(text_data=json.dumps({'error': 'Rate limit exceeded. Slow down.'}))
            return

        cache.set(cache_key, current_count + 1, timeout=1)

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
                is_private_media = data.get('is_private_media', False)
                media_url = data.get('media_url', None)
                reply_to_id = data.get('reply_to', None)
                try:
                    message = await self.save_message(text, reply_to_id=reply_to_id, is_private_media=is_private_media)
                except Exception as e:
                    await self.send(text_data=json.dumps({'error': str(e)}))
                    return

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message.text,
                        'sender': self.scope['user'].phone_number,
                        'sender_id': self.scope['user'].id,
                        'message_id': str(message.id),
                        'reply_to_id': reply_to_id,
                        'is_private_media': message.is_private_media,
                        'media_url': media_url
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
        # Dark Pattern: The "First Message Blur"
        # If receiver is not VIP and this is the first message interaction, mask the payload.
        message_content = event['message']
        room_type = await self.get_room_type()
        is_private_media = event.get('is_private_media', False)
        media_url = event.get('media_url')

        if room_type == 'PRIVATE' and self.scope['user'].phone_number != event['sender']:
            is_vip = await self.is_user_vip(self.scope['user'])
            if not is_vip:
                # Check if they have chatted before (more than 1 message means not the first interaction)
                msg_count = await self.get_room_message_count()
                # Blur logic: if it's the very first message they receive from someone
                if msg_count <= 1:
                    message_content = "🔒 [VIP REQUIRED] برای مشاهده این پیام اشتراک ویژه تهیه کنید."
                    media_url = None

            # Feature 2: Sunk-Cost Intimacy Progression
            if is_private_media:
                intimacy_level, current_points = await self.get_intimacy_level(event['sender_id'])
                if intimacy_level < 3:
                    media_url = None
                    message_content = f"🔒 [INTIMACY LEVEL 3 REQUIRED] سطح صمیمیت شما برای مشاهده این محتوای خصوصی کافی نیست. (سطح فعلی: {intimacy_level})"

        await self.send(text_data=json.dumps({
            'action': 'new_message',
            'message': message_content,
            'media_url': media_url,
            'sender': event['sender'],
            'message_id': event['message_id'],
            'reply_to_id': event.get('reply_to_id')
        }))

    async def broadcast_message(self, event):
        await self.send(text_data=json.dumps({
            'action': 'global_broadcast',
            'message': event['message']
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
            room = ChatRoom.objects.get(id=self.room_id)
            if room.room_type in ['GROUP', 'CHANNEL']:
                return room.members.filter(id=self.scope['user'].id).exists()

            # For PRIVATE rooms, ensure user is a member
            if room.room_type == 'PRIVATE':
                return room.members.filter(id=self.scope['user'].id).exists()

            return True
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def get_room_type(self):
        return ChatRoom.objects.get(id=self.room_id).room_type

    @database_sync_to_async
    def get_room_message_count(self):
        return ChatRoom.objects.get(id=self.room_id).messages.count()

    @database_sync_to_async
    def is_user_vip(self, user):
        from django.core.cache import cache
        # Check temporary VIP from Redis
        if cache.get(f'temp_vip_{user.id}'):
            return True
        return user.subscriptions.filter(is_active=True).exists()

    @database_sync_to_async
    def get_intimacy_level(self, sender_id):
        from chat.models import Intimacy
        u1, u2 = (self.scope['user'].id, sender_id) if self.scope['user'].id < sender_id else (sender_id, self.scope['user'].id)
        try:
            intimacy = Intimacy.objects.get(user_one_id=u1, user_two_id=u2)
            pts = intimacy.points
        except Intimacy.DoesNotExist:
            pts = 0

        if pts >= 1000:
            return 4, pts
        elif pts >= 500:
            return 3, pts
        elif pts >= 300:
            return 2, pts
        elif pts >= 100:
            return 1, pts
        return 0, pts

    @database_sync_to_async
    def is_room_admin(self):
        room = ChatRoom.objects.get(id=self.room_id)
        return room.admin == self.scope['user']

    @database_sync_to_async
    def save_message(self, text, reply_to_id=None, is_private_media=False):
        from core.models import SiteSettings
        room = ChatRoom.objects.get(id=self.room_id)

        # Allow the first message to be sent for free, but restrict replies if not premium based on settings.
        # The blurring is handled on the receiving end (chat_message).
        user_is_premium = self.scope['user'].subscriptions.filter(is_active=True).exists()

        if room.room_type == 'PRIVATE':
            # Check if this is the FIRST message in the room
            is_first_message = not room.messages.exists()

            settings = SiteSettings.load()

            if not is_first_message and not user_is_premium:
                other_user = room.members.exclude(id=self.scope['user'].id).first()
                other_user_is_premium = other_user.subscriptions.filter(is_active=True).exists() if other_user else False

                if settings.chat_reply_rule == 'premium_only':
                    raise Exception("برای ارسال پیام در این چت، باید حساب ویژه داشته باشید.")
                elif settings.chat_reply_rule == 'sender_premium' and not other_user_is_premium:
                    # If neither are premium
                    raise Exception("برای چت کردن باید حداقل یکی از طرفین حساب ویژه داشته باشد.")
        else:
            # Group/Channel
            if not user_is_premium:
                raise Exception("برای ارسال پیام در گروه یا کانال باید حساب ویژه داشته باشید.")


        reply_msg = None
        if reply_to_id:
            try:
                reply_msg = Message.objects.get(id=reply_to_id)
            except Message.DoesNotExist:
                pass

        msg = Message.objects.create(room=room, sender=self.scope['user'], text=text, reply_to=reply_msg, is_private_media=is_private_media)
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

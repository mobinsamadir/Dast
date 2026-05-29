import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Call
from subscriptions.models import Wallet
from django.utils import timezone
import asyncio

class WebRTCConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'call_{self.room_id}'
        self.user = self.scope['user']

        if self.user.is_anonymous:
            await self.close()
            return

        # Basic validation: check wallet balance
        balance = await self.get_wallet_balance(self.user)
        if balance < 10:
            await self.close(code=4002) # Custom code for insufficient funds
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Start billing task
        self.billing_task = asyncio.create_task(self.bill_user_periodically())

    async def disconnect(self, close_code):
        if hasattr(self, 'billing_task'):
            self.billing_task.cancel()

        if not self.scope['user'].is_anonymous:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Relay WebRTC signaling data (offer, answer, ice candidate)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_signal',
                'data': data,
                'sender_channel_name': self.channel_name
            }
        )

    async def webrtc_signal(self, event):
        # Don't send the signal back to the sender
        if self.channel_name != event['sender_channel_name']:
            await self.send(text_data=json.dumps(event['data']))

    async def bill_user_periodically(self):
        """Deducts coins every 60 seconds. Ends call if wallet is empty."""
        cost_per_minute = 20 # Can be fetched from settings/Call model
        try:
            while True:
                await asyncio.sleep(60) # Wait 1 minute
                success = await self.deduct_call_cost(self.user, cost_per_minute)
                if not success:
                    # Notify client to end call due to insufficient funds
                    await self.send(text_data=json.dumps({'type': 'end_call', 'reason': 'insufficient_funds'}))
                    await self.close()
                    break
        except asyncio.CancelledError:
            pass

    @database_sync_to_async
    def get_wallet_balance(self, user):
        try:
            return Wallet.objects.get(user=user).coin_balance
        except Wallet.DoesNotExist:
            return 0

    @database_sync_to_async
    def deduct_call_cost(self, user, amount):
        from subscriptions.utils import deduct_coins
        return deduct_coins(user, amount, 'Purchase', 'هزینه تماس تصویری (۱ دقیقه)')

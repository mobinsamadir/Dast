from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from chat.models import ChatRoom, Message
from subscriptions.models import Wallet
from admin_panel.models import FeatureFlag
from channels.testing import WebsocketCommunicator
from dastdoosti.asgi import application
from django.test import override_settings

@override_settings(SECURE_SSL_REDIRECT=False)
class ChatViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(phone_number='09123456789', password='password123', display_name='User1')
        self.user2 = CustomUser.objects.create_user(phone_number='09111111111', password='password123', display_name='User2')
        self.client.login(phone_number='09123456789', password='password123')

        # We don't create wallet again because signal handles it
        self.user.wallet.coin_balance = 500
        self.user.wallet.save()

        # Give subscription
        from subscriptions.models import Plan, Subscription
        from django.utils import timezone
        from datetime import timedelta
        plan = Plan.objects.create(name='Test Plan', duration_days=30, price=0)
        Subscription.objects.create(user=self.user, plan=plan, end_date=timezone.now() + timedelta(days=30))

    def test_chat_list(self):
        response = self.client.get(reverse('chat_list'))
        self.assertEqual(response.status_code, 200)

    def test_create_group(self):
        response = self.client.post(reverse('create_group'), {'name': 'Test Group'})
        self.assertEqual(response.status_code, 302)
        room = ChatRoom.objects.get(name='Test Group')
        self.assertEqual(room.room_type, 'GROUP')
        self.assertEqual(room.admin, self.user)
        self.user.wallet.refresh_from_db()
        self.assertEqual(self.user.wallet.coin_balance, 400) # 500 - 100

    def test_create_channel(self):
        response = self.client.post(reverse('create_channel'), {'name': 'Test Channel'})
        self.assertEqual(response.status_code, 302)
        room = ChatRoom.objects.get(name='Test Channel')
        self.assertEqual(room.room_type, 'CHANNEL')
        self.assertEqual(room.admin, self.user)
        self.user.wallet.refresh_from_db()
        self.assertEqual(self.user.wallet.coin_balance, 300) # 500 - 200

    def test_regex_filter(self):
        room = ChatRoom.objects.create(name='Test', room_type='PRIVATE')
        msg = Message.objects.create(room=room, sender=self.user, text='Call me 09123456789 or @test t.me/link https://google.com')
        self.assertTrue(msg.is_flagged)
        self.assertEqual(msg.text, 'Call me *** or *** *** ***')

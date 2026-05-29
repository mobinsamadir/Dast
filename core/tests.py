from django.test import TestCase, Client
from accounts.models import CustomUser
from subscriptions.models import Subscription, Plan, Wallet, GiftPacket
from chat.models import ChatRoom
from games.models import GameRoom
from calls.models import Call
from lottery.models import Lottery, Ticket
from notifications.models import Notification
from django.utils import timezone
from datetime import timedelta
import json
from django.test.utils import override_settings

@override_settings(SECURE_SSL_REDIRECT=False)
class APITests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            phone_number='09120000000',
            password='testpassword',
            first_name='Test',
            last_name='User',
            display_name='Test User',
            status='Active'
        )
        self.target = CustomUser.objects.create_user(
            phone_number='09130000000',
            password='testpassword',
            first_name='Target',
            last_name='User',
            display_name='Target User',
            status='Active'
        )
        self.client = Client()

        response = self.client.post('/api/v1/accounts/login/', {'phone_number': '09120000000', 'password': 'testpassword'}, content_type='application/json')
        if response.status_code == 200:
            self.token = response.json().get('access')
            self.auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        else:
            self.token = None
            self.auth_headers = {}

    def test_api_login(self):
        self.assertIsNotNone(self.token)

    def test_api_profile(self):
        if not self.token: return
        response = self.client.get('/api/v1/accounts/profile/', **self.auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_api_rooms(self):
        if not self.token: return
        response = self.client.get('/api/v1/chat/rooms/', **self.auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_api_games_lobby(self):
        if not self.token: return
        response = self.client.get('/api/v1/games/lobby/', **self.auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_api_lottery(self):
        if not self.token: return
        response = self.client.get('/api/v1/lottery/active/', **self.auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_swagger(self):
        response = self.client.get('/api/v1/docs/')
        self.assertIn(response.status_code, [200, 301, 302])

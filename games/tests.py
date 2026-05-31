from django.test import TestCase, Client
from accounts.models import CustomUser
from subscriptions.models import Subscription, Plan, Wallet
from games.models import GameRoom, TruthDareQuestion

from django.test import override_settings

@override_settings(SECURE_SSL_REDIRECT=False)
class GamesViewsTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            phone_number='09120000000',
            password='testpassword',
            first_name='Test',
            last_name='User',
            display_name='Test User'
        )
        self.client = Client()
        self.client.login(username='09120000000', password='testpassword')

        self.plan = Plan.objects.create(name='Test', duration_days=30, price=100)
        Subscription.objects.create(user=self.user, plan=self.plan, is_active=True, end_date='2030-01-01T00:00:00Z')

        wallet, _ = Wallet.objects.get_or_create(user=self.user)
        wallet.coin_balance = 1000
        wallet.save()

    def test_games_lobby_view(self):
        response = self.client.get('/games/')
        self.assertEqual(response.status_code, 200)

    def test_create_truth_dare_room(self):
        response = self.client.post('/games/truth-dare/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(GameRoom.objects.filter(game_type='TRUTH_DARE').exists())
        self.assertEqual(Wallet.objects.get(user=self.user).coin_balance, 990) # 10 deducted

    def test_single_player_correct(self):
        response = self.client.post('/games/single/', {'answer': 'CorrectAnswer123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Wallet.objects.get(user=self.user).coin_balance, 1005) # 5 rewarded

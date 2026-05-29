from django.test import TestCase, Client
from accounts.models import CustomUser
from subscriptions.models import Subscription, Plan, Wallet
from lottery.models import Lottery, Ticket
from django.utils import timezone
from datetime import timedelta

class LotteryViewsTests(TestCase):
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

        self.lottery = Lottery.objects.create(
            title='Test Lottery',
            prize_coins=1000,
            ticket_price=50,
            max_tickets_per_user=5,
            draw_date=timezone.now() + timedelta(days=1),
            is_active=True
        )

    def test_lottery_list_view(self):
        response = self.client.get('/lottery/')
        self.assertEqual(response.status_code, 200)

    def test_lottery_detail_view(self):
        response = self.client.get(f'/lottery/{self.lottery.id}/')
        self.assertEqual(response.status_code, 200)

    def test_buy_ticket(self):
        response = self.client.post(f'/lottery/{self.lottery.id}/buy/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ticket.objects.filter(user=self.user, lottery=self.lottery).exists())
        self.assertEqual(Wallet.objects.get(user=self.user).coin_balance, 950) # 50 deducted

    def test_my_tickets_view(self):
        response = self.client.get('/lottery/my-tickets/')
        self.assertEqual(response.status_code, 200)

    def test_winners_view(self):
        response = self.client.get('/lottery/winners/')
        self.assertEqual(response.status_code, 200)

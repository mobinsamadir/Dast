from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Wallet, CoinTransaction
from django.test.utils import override_settings

User = get_user_model()

@override_settings(SECURE_SSL_REDIRECT=False)
class WalletViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number='09111111111', password='testpassword123')
        self.url = reverse('wallet')
        self.client = Client()

    def test_unauthenticated_user_redirects(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        # Check that it redirects to login (typically /accounts/login/ by default in Django depending on LOGIN_URL)
        self.assertTrue('/login/' in response.url)

    def test_authenticated_user_without_wallet_creates_wallet(self):
        self.client.login(phone_number='09111111111', password='testpassword123')

        # Verify wallet doesn't exist yet
        self.assertFalse(Wallet.objects.filter(user=self.user).exists())

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        # Verify wallet was created
        self.assertTrue(Wallet.objects.filter(user=self.user).exists())
        wallet = Wallet.objects.get(user=self.user)

        self.assertTemplateUsed(response, 'subscriptions/wallet.html')
        self.assertEqual(response.context['wallet'], wallet)
        self.assertEqual(len(response.context['transactions']), 0)

    def test_authenticated_user_with_wallet_and_transactions(self):
        self.client.login(phone_number='09111111111', password='testpassword123')
        wallet = Wallet.objects.create(user=self.user)

        # Create some transactions
        t1 = CoinTransaction.objects.create(wallet=wallet, amount=10, transaction_type='Deposit', description='Test deposit 1')
        t2 = CoinTransaction.objects.create(wallet=wallet, amount=-5, transaction_type='Withdrawal', description='Test withdrawal')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wallet'], wallet)
        self.assertEqual(list(response.context['transactions']), [t2, t1])  # Ordered by -created_at

    def test_transaction_limit_to_10(self):
        self.client.login(phone_number='09111111111', password='testpassword123')
        wallet = Wallet.objects.create(user=self.user)

        # Create 15 transactions
        transactions = []
        for i in range(15):
            t = CoinTransaction.objects.create(wallet=wallet, amount=10, transaction_type='Deposit', description=f'Deposit {i}')
            transactions.append(t)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        # Should return exactly 10 transactions
        self.assertEqual(len(response.context['transactions']), 10)

        # Should be the most recent ones (the last 10 created, in reverse order)
        expected_transactions = transactions[-10:]
        expected_transactions.reverse()

        self.assertEqual(list(response.context['transactions']), expected_transactions)

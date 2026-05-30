from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from calls.models import Call
from subscriptions.models import Wallet
from django.test import override_settings

@override_settings(SECURE_SSL_REDIRECT=False)
class CallsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(phone_number='09123456789', password='password123', display_name='User1')
        self.user2 = CustomUser.objects.create_user(phone_number='09111111111', password='password123', display_name='User2')
        self.client.login(phone_number='09123456789', password='password123')

        self.user.wallet.coin_balance = 500
        self.user.wallet.save()

        from subscriptions.models import Plan, Subscription
        from django.utils import timezone
        from datetime import timedelta
        plan = Plan.objects.create(name='Test Plan', duration_days=30, price=0)
        Subscription.objects.create(user=self.user, plan=plan, end_date=timezone.now() + timedelta(days=30))

    def test_call_history(self):
        response = self.client.get(reverse('call_history'))
        self.assertEqual(response.status_code, 200)

    def test_initiate_call(self):
        response = self.client.get(reverse('initiate_call', args=[self.user2.id]))
        self.assertEqual(response.status_code, 302)
        call = Call.objects.first()
        self.assertEqual(call.caller, self.user)
        self.assertEqual(call.receiver, self.user2)

    def test_random_call_waiting(self):
        response = self.client.get(reverse('random_call_waiting'))
        self.assertEqual(response.status_code, 200)
        call = Call.objects.first()
        self.assertEqual(call.caller, self.user)
        self.assertIsNone(call.receiver)

        # Second user joins
        self.client.logout()
        self.client.login(phone_number='09111111111', password='password123')
        self.user2.wallet.coin_balance = 500
        self.user2.wallet.save()

        from subscriptions.models import Plan, Subscription
        from django.utils import timezone
        from datetime import timedelta
        plan = Plan.objects.first()
        Subscription.objects.create(user=self.user2, plan=plan, end_date=timezone.now() + timedelta(days=30))

        response2 = self.client.get(reverse('random_call_waiting'))
        self.assertEqual(response2.status_code, 302) # Should redirect to call room
        call.refresh_from_db()
        self.assertEqual(call.receiver, self.user2)

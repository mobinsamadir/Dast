from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from .models import Wallet, CoinPackage, Plan, GiftPacket, CoinTransaction, Subscription
from payments.models import PaymentTransaction
from django.test import override_settings

@override_settings(SECURE_SSL_REDIRECT=False)
class SubscriptionsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(phone_number='09123456789', password='password123', display_name='Test')
        self.receiver = CustomUser.objects.create_user(phone_number='09111111111', password='password123', display_name='Receiver')
        self.client.login(phone_number='09123456789', password='password123')

        self.package = CoinPackage.objects.create(name='Small', coins=100, price=10000)
        self.plan = Plan.objects.create(name='Vip', duration_days=30, price=50000)
        self.gift = GiftPacket.objects.create(name='Rose', coins=10, price=15, admin_commission_percent=10)

    def test_wallet_view(self):
        response = self.client.get(reverse('wallet'))
        self.assertEqual(response.status_code, 200)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    def test_upload_receipt(self):
        import io
        from PIL import Image
        from unittest.mock import patch

        file_obj = io.BytesIO()
        image = Image.new('RGB', (100, 100), color=(255, 0, 0))
        image.save(file_obj, format='JPEG')
        file_obj.seek(0)
        file_obj.name = 'test_img.jpg'

        with patch('core.tasks.image_tasks.process_uploaded_image.delay'):
            response = self.client.post(reverse('upload_receipt'), {
                'receipt_image': file_obj,
                'amount': 10000,
                'target_item': f'coins_{self.package.id}'
            })

        self.assertEqual(response.status_code, 302)
        payment = PaymentTransaction.objects.first()
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.target_item, f'coins_{self.package.id}')

    def test_send_gift(self):
        # Give user coins
        wallet = self.user.wallet
        wallet.coin_balance = 20
        wallet.save()

        response = self.client.post(reverse('send_gift', args=[self.receiver.id]), {
            'gift_id': self.gift.id
        })

        self.assertEqual(response.status_code, 302)

        self.user.wallet.refresh_from_db()
        self.receiver.wallet.refresh_from_db()

        self.assertEqual(self.user.wallet.coin_balance, 5) # 20 - 15
        self.assertEqual(self.receiver.wallet.coin_balance, 9) # 10 coins * 90% = 9

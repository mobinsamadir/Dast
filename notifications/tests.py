from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from .models import Notification
from django.test import override_settings

@override_settings(SECURE_SSL_REDIRECT=False)
class NotificationsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(phone_number='09123456789', password='password123', display_name='User1')
        self.client.login(phone_number='09123456789', password='password123')

        self.notif1 = Notification.objects.create(user=self.user, message='Test 1')
        self.notif2 = Notification.objects.create(user=self.user, message='Test 2')

    def test_notification_list(self):
        response = self.client.get(reverse('notifications_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['notifications']), 2)

    def test_mark_as_read(self):
        response = self.client.get(reverse('mark_notif_read', args=[self.notif1.id]))
        self.assertEqual(response.status_code, 302)
        self.notif1.refresh_from_db()
        self.assertTrue(self.notif1.is_read)

    def test_mark_all_as_read(self):
        response = self.client.get(reverse('mark_all_notifs_read'))
        self.assertEqual(response.status_code, 302)
        self.notif1.refresh_from_db()
        self.notif2.refresh_from_db()
        self.assertTrue(self.notif1.is_read)
        self.assertTrue(self.notif2.is_read)

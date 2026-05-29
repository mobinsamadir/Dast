from django.test import TestCase, Client
from django.contrib.auth import get_user_model
import json

User = get_user_model()


class HealthCheckViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/health/'
        self.unauthenticated_user = User.objects.create_user(
            password='password123',
            phone_number='+1234567890'
        )
        self.staff_user = User.objects.create_user(
            password='password123',
            phone_number='+1987654321',
            is_staff=True
        )

    def test_unauthenticated_access_returns_401(self):
        response = self.client.get(self.url, secure=True)
        # Handle trailing slash redirect if necessary
        if response.status_code == 301:
            response = self.client.get(response.url, secure=True)
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Authentication required')
        self.assertEqual(data['status'], 401)

    def test_authenticated_non_staff_returns_403(self):
        self.client.login(phone_number='+1234567890', password='password123')
        response = self.client.get(self.url, secure=True)
        if response.status_code == 301:
            response = self.client.get(response.url, secure=True)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Staff access required')
        self.assertEqual(data['status'], 403)

    def test_authenticated_staff_returns_200_and_data(self):
        self.client.login(phone_number='+1987654321', password='password123')
        response = self.client.get(self.url, secure=True)
        if response.status_code == 301:
            response = self.client.get(response.url, secure=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertIn('database', data)
        self.assertIn('ram_percent', data)
        self.assertIn('cpu_percent', data)
        self.assertIn('disk_percent', data)

from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
import uuid
from .models import user_directory_path, CustomUser
from django.test import override_settings

@override_settings(SECURE_SSL_REDIRECT=False)
class UserDirectoryPathTest(TestCase):

    @patch('accounts.models.uuid.uuid4')
    def test_standard_filename(self, mock_uuid):
        fixed_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
        mock_uuid.return_value = fixed_uuid
        result = user_directory_path(None, 'image.png')
        self.assertEqual(result, f'users/avatars/{fixed_uuid}.png')

    @patch('accounts.models.uuid.uuid4')
    def test_filename_with_multiple_dots(self, mock_uuid):
        fixed_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
        mock_uuid.return_value = fixed_uuid
        result = user_directory_path(None, 'my.cool.picture.jpg')
        self.assertEqual(result, f'users/avatars/{fixed_uuid}.jpg')

    @patch('accounts.models.uuid.uuid4')
    def test_filename_without_extension(self, mock_uuid):
        fixed_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
        mock_uuid.return_value = fixed_uuid
        result = user_directory_path(None, 'filename_no_ext')
        self.assertEqual(result, f'users/avatars/{fixed_uuid}.filename_no_ext')

@override_settings(SECURE_SSL_REDIRECT=False)
class AccountsAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(phone_number='09123456789', password='password123', first_name='Test', last_name='User', display_name='TestUser')

    def test_login(self):
        response = self.client.post(reverse('login'), {'phone_number': '09123456789', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('landing'))

    def test_login_invalid(self):
        response = self.client.post(reverse('login'), {'phone_number': '09123456789', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'شماره موبایل یا رمز عبور اشتباه است.')

    def test_password_reset_request(self):
        response = self.client.post(reverse('password_reset_request'), {'phone_number': '09123456789'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('password_reset_confirm'))
        self.assertEqual(self.client.session['reset_phone'], '09123456789')

    def test_password_reset_confirm(self):
        session = self.client.session
        session['reset_phone'] = '09123456789'
        session.save()
        response = self.client.post(reverse('password_reset_confirm'), {'new_password': 'newpassword123', 'new_password_confirm': 'newpassword123'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

@override_settings(SECURE_SSL_REDIRECT=False)
class RegistrationWizardTest(TestCase):
    def test_registration_wizard(self):
        client = Client()
        response = client.get(reverse('register_wizard'))
        self.assertEqual(response.status_code, 200)

        # Step 1
        data = {
            'registration_wizard-current_step': 'step1',
            'step1-phone_number': '09123456781',
            'step1-password': 'password123',
            'step1-password_confirm': 'password123',
        }
        response = client.post(reverse('register_wizard'), data)
        self.assertEqual(response.status_code, 200) # Should be on step 2

        # Step 2
        data = {
            'registration_wizard-current_step': 'step2',
            'step2-first_name': 'Test2',
            'step2-last_name': 'User2',
            'step2-display_name': 'TestUser2',
            'step2-gender': 'مرد',
            'step2-age': '25',
        }
        response = client.post(reverse('register_wizard'), data)
        self.assertEqual(response.status_code, 200) # Should be on step 3

        # Step 3
        data = {
            'registration_wizard-current_step': 'step3',
            'step3-marital_status': 'مجرد',
            'step3-children_count': 0,
            'step3-eldest_child_age': '',
        }
        response = client.post(reverse('register_wizard'), data)
        self.assertEqual(response.status_code, 200)

        # Step 4
        data = {
            'registration_wizard-current_step': 'step4',
            'step4-height': '180',
            'step4-weight': '75',
            'step4-skin_color': 'سفید',
            'step4-beauty': 4,
            'step4-style': 'سایر',
            'step4-health_status': 'Good',
        }
        response = client.post(reverse('register_wizard'), data)
        self.assertEqual(response.status_code, 200)

        # Step 5
        data = {
            'registration_wizard-current_step': 'step5',
            'step5-income': 'کمتر از ۱۰ میلیون تومان',
            'step5-car_status': 'ندارم',
            'step5-housing_status': 'اجاره‌ای',
            'step5-lifestyle': 'مستقل',
        }
        response = client.post(reverse('register_wizard'), data)
        self.assertEqual(response.status_code, 200)

        # Step 6
        data = {
            'registration_wizard-current_step': 'step6',
            'step6-province': 'تهران',
            'step6-city': 'تهران',
            'step6-location_lat': '35.6892',
            'step6-location_lng': '51.3890',
            'step6-show_location': 'on',
        }
        response = client.post(reverse('register_wizard'), data)
        self.assertEqual(response.status_code, 200)

        # Step 7
        data = {
            'registration_wizard-current_step': 'step7',
            'step7-bio': 'Hello World',
            'step7-spouse_expectation': 'Nothing',
            'step7-seeking': 'دوست',
            'step7-target_gender': 'زن',
            'step7-security_phrase': 'Cat',
            'step7-referral_code': '',
        }
        response = client.post(reverse('register_wizard'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('landing'))

        user = CustomUser.objects.get(phone_number='09123456781')
        self.assertEqual(user.first_name, 'Test2')
        self.assertEqual(user.city, 'تهران')

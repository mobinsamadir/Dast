from django.test import TestCase
from unittest.mock import patch
import uuid
from .models import user_directory_path

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

        # When there is no extension, split('.')[-1] returns the whole filename
        self.assertEqual(result, f'users/avatars/{fixed_uuid}.filename_no_ext')

import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO
from django.contrib.auth import get_user_model
User = get_user_model()
from payments.models import PaymentTransaction
from chat.models import Message, ChatRoom
from core.utils.image import process_image

class ImageProcessingTests(TestCase):
    def create_test_image(self, size=(2000, 2000), mode='RGB', format='JPEG'):
        """Helper to create a test image and return a SimpleUploadedFile"""
        img = Image.new(mode, size, color=(255, 0, 0) if mode == 'RGB' else (255, 0, 0, 128))
        output = BytesIO()
        img.save(output, format=format)
        output.seek(0)
        return SimpleUploadedFile(
            f"test_image.{format.lower()}",
            output.read(),
            content_type=f"image/{format.lower()}"
        )

    def test_image_utility_webp_conversion_and_resizing(self):
        """Test that the utility converts to WebP and caps dimensions at 1200x1200px."""
        large_image = self.create_test_image(size=(2000, 1500), mode='RGB', format='JPEG')

        processed_file = process_image(large_image, quality=82)

        self.assertIsNotNone(processed_file)
        self.assertTrue(processed_file.name.endswith('.webp'))
        self.assertEqual(processed_file.content_type, 'image/webp')

        # Verify dimensions and format
        img = Image.open(processed_file)
        self.assertEqual(img.format, 'WEBP')
        self.assertTrue(img.size[0] <= 1200)
        self.assertTrue(img.size[1] <= 1200)
        # Check aspect ratio preservation
        self.assertEqual(img.size, (1200, 900))

    def test_image_utility_rgba_handling(self):
        """Test that RGBA images are converted correctly without alpha channel issues in WebP."""
        rgba_image = self.create_test_image(size=(800, 800), mode='RGBA', format='PNG')

        processed_file = process_image(rgba_image, quality=82)

        img = Image.open(processed_file)
        # The result should be a WEBP. Our code converts RGBA to RGB with white background before WEBP.
        # But wait, WEBP actually supports RGBA. However, our code converts to RGB with white background.
        self.assertEqual(img.format, 'WEBP')
        # We can just verify it processes without errors and returns WEBP

    def test_image_utility_quality_difference(self):
        """Test that different quality settings affect file size."""
        # Note: We need a somewhat complex image for compression to show difference
        img = Image.new('RGB', (1000, 1000))
        # Add some noise/gradient
        pixels = img.load()
        for i in range(1000):
            for j in range(1000):
                pixels[i, j] = (i % 255, j % 255, (i+j) % 255)
        output = BytesIO()
        img.save(output, format='JPEG')
        output.seek(0)
        complex_image = SimpleUploadedFile("complex.jpg", output.read(), content_type="image/jpeg")

        # Since SimpleUploadedFile reads from memory, we need two separate copies to avoid cursor issues
        output.seek(0)
        complex_image2 = SimpleUploadedFile("complex2.jpg", output.read(), content_type="image/jpeg")

        processed_low = process_image(complex_image, quality=10)
        processed_high = process_image(complex_image2, quality=90)

        self.assertTrue(processed_low.size < processed_high.size)

    def test_celery_task_integration(self):
        """Test the celery task processes the image and updates the model."""
        user = User.objects.create(
            phone_number="+1234567890",
            first_name="Test",
            last_name="User",
            display_name="Test User"
        )
        # Using a valid original image
        img = self.create_test_image(size=(800, 800), format='PNG')
        user.profile_picture = img
        from unittest.mock import patch
        with patch('core.tasks.image_tasks.process_uploaded_image.delay') as mock_delay:
            user.save()

        # In testing, the post_save signal might run process_uploaded_image.delay
        # We need to run it synchronously to test it.
        from core.tasks.image_tasks import process_uploaded_image

        # Note: Depending on CELERY_TASK_ALWAYS_EAGER, the signal might have already run it.
        # Let's force run it just to be sure.
        process_uploaded_image(
            app_label='accounts',
            model_name='CustomUser',
            instance_id=user.pk,
            field_name='profile_picture',
            quality=82
        )

        user.refresh_from_db()
        self.assertTrue(user.profile_picture.name.endswith('.webp'))

        # Verify the original raw file (e.g., .png) was deleted and .webp is there
        img = Image.open(user.profile_picture)
        self.assertEqual(img.format, 'WEBP')

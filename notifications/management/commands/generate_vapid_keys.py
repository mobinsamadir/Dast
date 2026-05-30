from django.core.management.base import BaseCommand
import base64
import os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

class Command(BaseCommand):
    help = 'Generate VAPID keys for Web Push Notifications'

    def handle(self, *args, **options):
        # Generate private key
        private_key = ec.generate_private_key(ec.SECP256R1())

        # Serialize private key
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        private_key_b64 = base64.urlsafe_b64encode(private_bytes).decode('utf-8').rstrip('=')

        # Generate public key
        public_key = private_key.public_key()

        # Serialize public key
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        public_key_b64 = base64.urlsafe_b64encode(public_bytes).decode('utf-8').rstrip('=')

        self.stdout.write(self.style.SUCCESS('VAPID Keys generated successfully!\n'))
        self.stdout.write(self.style.WARNING('Add these to your .env file:\n'))
        self.stdout.write(f'VAPID_PUBLIC_KEY={public_key_b64}')
        self.stdout.write(f'VAPID_PRIVATE_KEY={private_key_b64}')

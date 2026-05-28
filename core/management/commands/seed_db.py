from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with test data'

    def handle(self, *args, **options):
        if not User.objects.filter(phone_number='09000000000').exists():
            User.objects.create_superuser(phone_number='09000000000', password='admin')
            self.stdout.write(self.style.SUCCESS('Successfully created superuser (phone: 09000000000, pass: admin)'))

        if not User.objects.filter(phone_number='09111111111').exists():
            User.objects.create_user(phone_number='09111111111', password='testuser')
            self.stdout.write(self.style.SUCCESS('Successfully created test user (phone: 09111111111, pass: testuser)'))

        self.stdout.write(self.style.SUCCESS('Database seeded successfully'))

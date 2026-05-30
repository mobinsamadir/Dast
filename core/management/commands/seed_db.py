from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from subscriptions.models import Plan, CoinPackage, Subscription, Wallet
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with test data'

    def handle(self, *args, **options):
        # Create users
        if not User.objects.filter(phone_number='09000000000').exists():
            User.objects.create_superuser(
                phone_number='09000000000',
                password='admin',
                first_name='Admin',
                last_name='User',
                display_name='Admin'
            )
            self.stdout.write(self.style.SUCCESS('Successfully created superuser (phone: 09000000000, pass: admin)'))

        test_user, test_user_created = User.objects.get_or_create(
            phone_number='09111111111',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'display_name': 'TestUser',
                'status': 'Active'
            }
        )
        if test_user_created:
            test_user.set_password('testuser')
            test_user.save()
            self.stdout.write(self.style.SUCCESS('Successfully created test user (phone: 09111111111, pass: testuser)'))

        # Create basic plan and package
        plan, _ = Plan.objects.get_or_create(
            name='اشتراک یک ماهه',
            defaults={
                'description': 'دسترسی کامل به تمام امکانات سایت برای یک ماه.',
                'duration_days': 30,
                'price': 50000
            }
        )

        CoinPackage.objects.get_or_create(
            name='بسته ۵۰۰ سکه‌ای',
            defaults={'coins': 500, 'price': 20000}
        )

        # Assign plan and coins to test user
        if not Subscription.objects.filter(user=test_user, is_active=True).exists():
            Subscription.objects.create(
                user=test_user,
                plan=plan,
                end_date=timezone.now() + timedelta(days=30),
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS('Added active subscription to test user'))

        wallet, _ = Wallet.objects.get_or_create(user=test_user)
        if wallet.coin_balance < 500:
            wallet.coin_balance += 1000
            wallet.save()
            self.stdout.write(self.style.SUCCESS('Added 1000 coins to test user wallet'))

        self.stdout.write(self.style.SUCCESS('Database seeded successfully'))

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from chat.models import ChatRoom, Message
import uuid
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Injects weaponized bots and targets active users based on their interested_in array to trigger FOMO.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=5, help='Number of bots to create')
        parser.add_argument('--gender', type=str, choices=['زن', 'مرد', 'ترنس'], default='زن', help='Gender of the bots')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        gender = kwargs['gender']

        bot_names = {
            'زن': ['سارا', 'مهسا', 'نگار', 'آیناز', 'نیلوفر'],
            'مرد': ['آرش', 'علی', 'سامان', 'کامران', 'پوریا'],
            'ترنس': ['رها', 'شادی', 'نفس', 'امید']
        }

        # 1. Spawn Bots
        bots = []
        for i in range(count):
            phone = f"0999BOT{uuid.uuid4().hex[:4].upper()}"
            name = random.choice(bot_names.get(gender, ['Bot']))

            bot, created = User.objects.get_or_create(
                phone_number=phone,
                defaults={
                    'first_name': name,
                    'last_name': 'Bot',
                    'display_name': f"{name} 🎀",
                    'gender': gender,
                    'status': 'فعال',
                    'is_bot_verified': True,  # Fake verification
                    'beauty': 5,
                    'bio': 'دنبال یه رابطه جدی و پر هیجان هستم. پیام بده تا بیشتر آشنا بشیم.'
                }
            )
            bot.set_password("botpassword123")
            bot.save()
            bots.append(bot)
            self.stdout.write(self.style.SUCCESS(f'Created Bot: {bot.display_name} ({gender})'))

        # 2. Target Real Users
        # Find users who are NOT VIP (to trigger the blur effect) and are interested in the bot's gender
        real_users = User.objects.exclude(phone_number__contains='BOT').filter(
            interested_in__contains=[gender],
            status='فعال'
        )

        hook_messages = [
            "سلام، پروفایلت رو دیدم خیلی خوشم اومد. میای بیشتر آشنا بشیم؟ 😉",
            "چطوری؟ به نظرم آدم جالبی میای... دوست داری چت کنیم؟",
            "سلام عزیزم، وقتت بخیر. من تازه اومدم اینجا. میشه راهنماییم کنی؟ 🙈"
        ]

        messages_sent = 0
        for user in real_users:
            is_vip = user.subscriptions.filter(is_active=True).exists()
            if not is_vip:
                # Select a random bot
                bot = random.choice(bots)

                # Check if room already exists to avoid spamming the same user
                room_exists = ChatRoom.objects.filter(room_type='PRIVATE', members=user).filter(members=bot).exists()
                if not room_exists:
                    room = ChatRoom.objects.create(room_type='PRIVATE', name=f"چت {bot.display_name} و {user.display_name}")
                    room.members.add(bot, user)

                    # Send the hook message
                    text = random.choice(hook_messages)
                    Message.objects.create(room=room, sender=bot, text=text)
                    messages_sent += 1

                    self.stdout.write(f'Targeted {user.phone_number} with Bot {bot.display_name}')

        self.stdout.write(self.style.SUCCESS(f'\nSuccess! Injected {count} bots. Sent {messages_sent} FOMO messages to non-VIP targets.'))

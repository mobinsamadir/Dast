from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.core.cache import cache
import random
from datetime import timedelta
from .serializers import PlanSerializer, WalletSerializer, TransactionSerializer
from subscriptions.models import Plan, Wallet, CoinTransaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from subscriptions.utils import add_coins

class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_control(public=True, max_age=3600))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class WalletView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return wallet

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return CoinTransaction.objects.filter(wallet=wallet).order_by('-created_at')

class DailyGachaSpinView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        now = timezone.now()

        # Check cooldown (24 hours)
        if user.last_spin_date and now < user.last_spin_date + timedelta(hours=24):
            time_left = (user.last_spin_date + timedelta(hours=24)) - now
            return Response({'error': f'لطفا {time_left.seconds // 3600} ساعت دیگر تلاش کنید.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Update last spin date
        user.last_spin_date = now
        user.save(update_fields=['last_spin_date'])

        # Spin Logic
        rewards = [
            {'type': 'coins', 'amount': 10, 'weight': 50},
            {'type': 'coins', 'amount': 50, 'weight': 30},
            {'type': 'coins', 'amount': 100, 'weight': 10},
            {'type': 'vip', 'duration_minutes': 15, 'weight': 10},
        ]

        choices = [r for r in rewards]
        weights = [r['weight'] for r in rewards]
        selected_reward = random.choices(choices, weights=weights, k=1)[0]

        if selected_reward['type'] == 'coins':
            add_coins(user, selected_reward['amount'], 'Game', 'برنده شدن در گردونه شانس روزانه')
            message = f"شما {selected_reward['amount']} سکه برنده شدید!"
        elif selected_reward['type'] == 'vip':
            cache.set(f'temp_vip_{user.id}', True, timeout=selected_reward['duration_minutes'] * 60)
            message = f"شما {selected_reward['duration_minutes']} دقیقه اشتراک ویژه برنده شدید!"

        return Response({'message': message, 'reward': selected_reward}, status=status.HTTP_200_OK)

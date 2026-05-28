from rest_framework import generics, permissions
from .serializers import PlanSerializer, WalletSerializer, TransactionSerializer
from subscriptions.models import Plan, Wallet, CoinTransaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

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
        return Wallet.objects.get(user=self.request.user)

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        wallet = Wallet.objects.get(user=self.request.user)
        return CoinTransaction.objects.filter(wallet=wallet).order_by('-created_at')

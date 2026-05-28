from rest_framework import generics, permissions
from .serializers import LotterySerializer
from lottery.models import Lottery
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

class LotteryListView(generics.ListAPIView):
    serializer_class = LotterySerializer
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(cache_control(public=True, max_age=300))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Lottery.objects.filter(is_active=True)

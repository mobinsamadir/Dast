from drf_spectacular.utils import extend_schema

from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from .serializers import UserSerializer, RegisterSerializer
from accounts.models import CustomUser
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from rest_framework.decorators import api_view, permission_classes
from accounts.utils import get_haversine_expression
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class CustomAnonThrottle(AnonRateThrottle):
    rate = '10/h'

class CustomUserThrottle(UserRateThrottle):
    rate = '1000/day'

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [CustomAnonThrottle]

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [CustomUserThrottle]

    def get_object(self):
        return self.request.user

    @method_decorator(cache_control(public=True, max_age=300))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@extend_schema(responses={200: UserSerializer(many=True)})
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@cache_control(public=True, max_age=300)
def nearby_users(request):
    if not request.user.show_location or request.user.location_lat is None or request.user.location_lng is None:
        return Response({'detail': 'موقعیت مکانی شما فعال یا ثبت نشده است.'}, status=400)

    users = CustomUser.objects.filter(
        show_location=True,
        location_lat__isnull=False,
        location_lng__isnull=False
    ).exclude(status='Blocked').exclude(id=request.user.id)

    users = users.annotate(
        distance=get_haversine_expression(request.user.location_lat, request.user.location_lng)
    ).order_by('distance')[:20]

    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

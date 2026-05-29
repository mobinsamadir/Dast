from drf_spectacular.utils import extend_schema

from rest_framework import generics, permissions
from rest_framework.response import Response
from .serializers import UserSerializer, RegisterSerializer
from accounts.models import CustomUser
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from rest_framework.decorators import api_view, permission_classes

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    @method_decorator(cache_control(public=True, max_age=300))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@api_view(['GET'])

@extend_schema(responses={200: UserSerializer(many=True)})
@permission_classes([permissions.IsAuthenticated])
@cache_control(public=True, max_age=300)
def nearby_users(request):
    # Mock implementation of nearby users
    users = CustomUser.objects.filter(status='Active').exclude(id=request.user.id)[:10]
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

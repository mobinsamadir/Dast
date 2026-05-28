from rest_framework import generics, permissions
from .serializers import CallSerializer
from calls.models import Call

class CallHistoryView(generics.ListAPIView):
    serializer_class = CallSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Call.objects.filter(caller=self.request.user) | Call.objects.filter(receiver=self.request.user)

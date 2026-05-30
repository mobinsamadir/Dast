from drf_spectacular.utils import extend_schema

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from chat.models import Message
from chat.api.serializers import MessageSerializer
from django.utils.dateparse import parse_datetime

@extend_schema(responses={200: dict})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_view(request):
    """
    Offline sync endpoint.
    Takes a ?since= ISO-8601 timestamp and returns all updates since then.
    """
    since_str = request.query_params.get('since')
    if not since_str:
        return Response({"error": "Query parameter 'since' is required."}, status=400)

    since_dt = parse_datetime(since_str)
    if not since_dt:
        return Response({"error": "Invalid timestamp format."}, status=400)

    # Example: fetch new messages for user's rooms since timestamp
    rooms = request.user.chat_rooms.all()
    messages = Message.objects.filter(room__in=rooms, timestamp__gte=since_dt)
    msg_serializer = MessageSerializer(messages, many=True)

    # Example: could also fetch notifications, transactions, etc.

    data = {
        "messages": msg_serializer.data,
        "notifications": [], # Mock
        "wallet_updates": [] # Mock
    }

    return Response(data)

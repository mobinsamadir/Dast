from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from calls.models import Call
from django.shortcuts import get_object_or_404

@extend_schema(responses={200: dict})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def call_status_view(request, room_id):
    call = get_object_or_404(Call, id=room_id)
    return Response({
        'status': call.status,
        'receiver_id': call.receiver.id if call.receiver else None
    })

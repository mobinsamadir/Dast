from rest_framework import serializers
from games.models import GameRoom

class GameRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRoom
        fields = '__all__'

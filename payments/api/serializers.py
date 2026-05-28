from rest_framework import serializers
from payments.models import PaymentTransaction

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = '__all__'
        read_only_fields = ['user', 'status', 'created_at', 'approved_at']

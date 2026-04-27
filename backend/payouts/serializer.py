from .models import Payout
from rest_framework import serializers
from merchants.serializer import MerchantSerializer, BankAccountSerializer

class PayoutRequestSerializer(serializers.Serializer):
    bank_account_id = serializers.UUIDField()
    amount_paise = serializers.BigIntegerField(min_value=1)

class PayoutResponseSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format='hex_verbose')
    merchant = MerchantSerializer()
    bank_account = BankAccountSerializer()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    
    class Meta:
        model=Payout
        fields=['id', 'merchant', 'amount_paise', 'bank_account', 'status', 'created_at', 'updated_at', 'task_id', 'failure_reason', 'attempts', 'last_attempted_at']
        read_only_fields=['id', 'created_at', 'updated_at']
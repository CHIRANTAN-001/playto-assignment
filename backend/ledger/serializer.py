from rest_framework import serializers
from .models import Ledger
from merchants.serializer import MerchantSerializer

class LedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ledger
        fields = ['id', 'entry_type', 'amount_paise', 'description', 'created_at']
        read_only_fields=['id', 'created_at']

class LedgerResponseSerializer(serializers.ModelSerializer):
    merchant = MerchantSerializer()
    class Meta:
        model = Ledger
        fields = ['id', 'entry_type', 'amount_paise', 'merchant', 'payout_id', 'description', 'created_at']
        read_only_fields=['id', 'created_at']
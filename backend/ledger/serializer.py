from rest_framework import serializers
from .models import Ledger

class LedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ledger
        fields = ['id', 'entry_type', 'amount_paise', 'description', 'reference_note', 'created_at']
        read_only_fields=['id', 'created_at']
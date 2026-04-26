from .models import Payout
from rest_framework import serializers

class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = ['id', 'merchant', 'amount_paise', 'bank_account', 'status', 'attempts', 'last_attempted_at', 'failure_reason', 'task_id', 'created_at', 'updated_at']
        read_only_fields=['id', 'created_at', 'updated_at']
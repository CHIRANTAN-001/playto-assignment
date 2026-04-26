from rest_framework import serializers
from .models import Merchant, BankAccount

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model=BankAccount
        fields=['id', 'account_number', 'merchant', 'created_at']
        read_only_fields=['id', 'created_at']

class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ['id', 'name', 'email', 'created_at']
        read_only_fields=['id', 'created_at']
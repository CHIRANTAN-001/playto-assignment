from rest_framework import serializers
from .models import Merchant, BankAccount

class BankAccountSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(format='hex_verbose')
    class Meta:
        model=BankAccount
        fields=['id', 'account_number']
        read_only_fields=['id']

class MerchantSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(format='hex_verbose')
    class Meta:
        model = Merchant
        fields = ['id', 'name', 'email']
        read_only_fields=['id']
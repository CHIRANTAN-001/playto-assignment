from rest_framework import serializers
from .models import Merchant, BankAccount

class BankAccountSerializer(serializers.ModelSerializer):
    masked_account_number = serializers.SerializerMethodField()

    class Meta:
        model = BankAccount
        fields = ["id", "masked_account_number"]

    def get_masked_account_number(self, obj):
        acc = obj.account_number
        if len(acc) <= 4:
            return acc
        return "*" * (len(acc) - 4) + acc[-4:]

class MerchantSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(format='hex_verbose')
    class Meta:
        model = Merchant
        fields = ['id', 'name', 'email']
        read_only_fields=['id']


class MerchantLookupSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
from .models import Merchant, BankAccount
from .serializer import MerchantSerializer, BankAccountSerializer
from django.core.exceptions import ValidationError
from django.db import transaction

def create_merchant(name: str, email: str) -> Merchant:
    return Merchant.objects.create(name=name, email=email)


def create_bank_account(merchant: Merchant, account_number: str) -> BankAccount:
    if not account_number:
        raise ValidationError("Account number is required")

    account_number = account_number.strip()

    # optional: basic validation (customize as needed)
    if not account_number.isdigit():
        raise ValidationError("Account number must be numeric")

    # DB-level UniqueConstraint on account_number prevents duplicates
    if BankAccount.objects.filter(account_number=account_number).exists():
        raise ValidationError("Bank account with this number already exists")

    return BankAccount.objects.create(
        merchant=merchant,
        account_number=account_number
    )

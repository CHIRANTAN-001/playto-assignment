from .models import Merchant, BankAccount
from .serializer import MerchantSerializer, BankAccountSerializer


def create_merchant(name: str, email: str) -> Merchant:
    return Merchant.objects.create(name=name, email=email)


def create_bank_account(merchant: Merchant, account_number: str) -> BankAccount:
    return BankAccount.objects.create(merchant=merchant, account_number=account_number)

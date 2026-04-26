from .models import Payout
from django.db import transaction
from ledger.models import Ledger
from ledger.services import get_available_balance_for_update
from merchants.models import Merchant, BankAccount
from idempotencykey.models import IdempotencyKey
from idempotencykey.services import create_idempotency_key, update_idempotency_key, get_idempotency_key
from .serializer import PayoutResponseSerializer

class InSufficientFunds(Exception):
    pass
class InvalidBankAccount(Exception):
    pass
class ConflictIdempotencyKey(Exception):
    pass

def create_payout(idempotency_key: str, amount_paise: int, bank_account_id: str) -> Payout | dict | None:
    with transaction.atomic():
         # 1. get bank account and derive merchant
        try:
            bank_account = BankAccount.objects.get(account_number=bank_account_id)
        except BankAccount.DoesNotExist:
            raise InvalidBankAccount

        merchant = bank_account.merchant
        print(merchant)
        
        # 2. check idempotency key
        existing_key = get_idempotency_key(
            key=idempotency_key,
            merchant=merchant
        )
        
        if existing_key is not None:
            if existing_key.in_flight:
                raise ConflictIdempotencyKey
            return existing_key.response_body # type: ignore
        
        # 3. key doesn't exist — create it (in_flight=True)
        idempotency_record = create_idempotency_key(
            key=idempotency_key,
            merchant=merchant
        )

        # 4. balance check
        balance = get_available_balance_for_update(merchant.id)
        if balance < amount_paise:
            raise InSufficientFunds
        
        # 5. create payout
        payout = Payout.objects.create(
            amount_paise=amount_paise,
            bank_account=bank_account,
            merchant=merchant,
        )

        # 6. create debit ledger entry
        Ledger.objects.create(
            merchant=merchant,
            entry_type='debit',
            amount_paise=amount_paise,
            description='Payout hold',
            payout=payout
        )
        
        # 7. mark idempotency key as complete
        response_data = PayoutResponseSerializer(payout).data
        update_idempotency_key(
            idempotency_key=idempotency_record,
            response_status=202,
            response_body=dict(response_data)
        )
        
        return payout



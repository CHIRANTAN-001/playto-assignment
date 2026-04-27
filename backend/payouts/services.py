from .models import Payout
from django.db import transaction
from django.utils import timezone
from ledger.models import Ledger
from ledger.services import get_available_balance_for_update, get_available_balance
from merchants.models import Merchant, BankAccount
from idempotencykey.models import IdempotencyKey
from idempotencykey.services import create_idempotency_key, update_idempotency_key, get_idempotency_key
from .serializer import PayoutResponseSerializer
from .tasks import process_payout

class InSufficientFunds(Exception):
    pass
class InvalidBankAccount(Exception):
    pass
class ConflictIdempotencyKey(Exception):
    pass

def schedule_payout(payout_id: str) -> None:
    task = process_payout.delay(str(payout_id)) # type: ignore[attr-defined]
    Payout.objects.filter(id=payout_id).update(task_id=str(task.id))

def create_payout(idempotency_key: str, amount_paise: int, bank_account_id: str) -> Payout | dict | None:
    with transaction.atomic():
         # 1. get bank account and derive merchant
        try:
            bank_account = BankAccount.objects.get(id=bank_account_id)
        except BankAccount.DoesNotExist:
            raise InvalidBankAccount()

        merchant = Merchant.objects.select_for_update().get(id=bank_account.merchant.id)
        
        # 2. check idempotency key
        existing_key = get_idempotency_key(
            key=idempotency_key,
            merchant=merchant,
        )
        
        if existing_key is not None:
            age = timezone.now() - existing_key.created_at
            if age.total_seconds() < 86400:
                if existing_key.in_flight:
                    raise ConflictIdempotencyKey()
            return existing_key.response_body
        
        # 3. key doesn't exist — create it (in_flight=True)
        idempotency_record = create_idempotency_key(
            key=idempotency_key,
            merchant=merchant
        )

        # 4. balance check
        balance = get_available_balance(merchant_id=str(merchant.id))
        if balance < amount_paise:
            raise InSufficientFunds()
        
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
        
        transaction.on_commit(lambda: schedule_payout(str(payout.id)))
        
        return payout


def get_payout(payout_id: str) -> Payout | None:
    return Payout.objects.filter(id=payout_id).first()
from .models import Payout
from django.db import transaction
from django.utils import timezone
from ledger.models import Ledger
from ledger.services import get_available_balance
from merchants.models import Merchant, BankAccount
from idempotencykey.models import IdempotencyKey
from idempotencykey.services import create_idempotency_key, update_idempotency_key, get_idempotency_key
from .serializer import PayoutResponseSerializer
from .tasks import process_payout
from django.db.models import Sum, Case, When, F, Value, BigIntegerField
from django.db.models.functions import Coalesce
import logging

logger = logging.getLogger(__name__)

class InSufficientFunds(Exception):
    pass
class InvalidBankAccount(Exception):
    pass
class ConflictIdempotencyKey(Exception):
    pass
class IncorrectMerchant(Exception):
    pass

def schedule_payout(payout_id: str) -> None:
    task = process_payout.delay(str(payout_id)) # type: ignore[attr-defined]
    Payout.objects.filter(id=payout_id).update(task_id=str(task.id))
    logger.info(f"[schedule_payout] payout_id={payout_id} dispatched as celery task_id={task.id}")

def create_payout(idempotency_key: str, amount_paise: int, bank_account_id: str) -> Payout | dict | None:
    logger.info(f"[create_payout] Starting — idempotency_key={idempotency_key} amount_paise={amount_paise} bank_account_id={bank_account_id}")
    
    with transaction.atomic():
         # 1. get bank account and derive merchant
        try:
            bank_account = BankAccount.objects.get(id=bank_account_id)
        except BankAccount.DoesNotExist:
            logger.warning(f"[create_payout] Invalid bank_account_id={bank_account_id}")
            raise InvalidBankAccount()

        merchant = Merchant.objects.select_for_update().get(id=bank_account.merchant.id)
        logger.info(f"[create_payout] Resolved merchant_id={merchant.id} ({merchant.name})")
        
        # 2. check idempotency key
        existing_key = get_idempotency_key(
            key=idempotency_key,
            merchant=merchant,
        )
        
        if existing_key is not None:
            age = timezone.now() - existing_key.created_at
            if age.total_seconds() < 86400:
                if existing_key.in_flight:
                    logger.warning(f"[create_payout] Idempotency key '{idempotency_key}' is in-flight — conflict")
                    raise ConflictIdempotencyKey()
                else:
                    logger.info(f"[create_payout] Idempotency key '{idempotency_key}' replay — returning cached response")
                    return existing_key.response_body
        
        # 3. key doesn't exist — create it (in_flight=True)
        idempotency_record = create_idempotency_key(
            key=idempotency_key,
            merchant=merchant
        )

        # 4. balance check
        balance = get_available_balance(merchant_id=str(merchant.id))
        if balance < amount_paise:
            logger.warning(f"[create_payout] Insufficient funds — merchant_id={merchant.id} available={balance} requested={amount_paise}")
            raise InSufficientFunds()
        
        # 5. create payout
        payout = Payout.objects.create(
            amount_paise=amount_paise,
            bank_account=bank_account,
            merchant=merchant,
        )
        logger.info(f"[create_payout] Payout created — payout_id={payout.id} amount_paise={amount_paise}")

        # 6. create debit ledger entry
        Ledger.objects.create(
            merchant=merchant,
            entry_type='debit',
            amount_paise=amount_paise,
            description='Payout hold',
            payout=payout
        )
        logger.info(f"[create_payout] Debit hold recorded — merchant_id={merchant.id} amount_paise={amount_paise}")
        
        # 7. mark idempotency key as complete
        response_data = PayoutResponseSerializer(payout).data
        update_idempotency_key(
            idempotency_key=idempotency_record,
            response_status=202,
            response_body=dict(response_data)
        )
        
        transaction.on_commit(lambda pid=payout.id: schedule_payout(str(pid)))
        
        logger.info(f"[create_payout] Payout {payout.id} committed — scheduled for async processing")
        return payout


def get_payout(payout_id: str) -> Payout | None:
    return Payout.objects.filter(id=payout_id).first()

def get_merchant_payouts(merchant_id: str, cursor: str | None = None, page_size: int = 20):
    try:
        merchant = Merchant.objects.get(id=merchant_id)
    except Merchant.DoesNotExist:
        logger.warning(f"[get_merchant_payouts] Merchant not found — merchant_id={merchant_id}")
        raise IncorrectMerchant()

    qs = Payout.objects.filter(merchant=merchant).select_related("bank_account").order_by("-id")

    if cursor:
        qs = qs.filter(id__lt=cursor)

    payouts = list(qs[:page_size + 1])

    has_next = len(payouts) > page_size
    if has_next:
        payouts = payouts[:page_size]

    return {
        "results": payouts,
        "next_cursor": str(payouts[-1].id) if has_next and payouts else None,
        "has_next": has_next,
    }


def get_merchant_ledgers(merchant_id: str, cursor: str | None = None, page_size: int = 20):
    try:
        merchant = Merchant.objects.get(id=merchant_id)
    except Merchant.DoesNotExist:
        logger.warning(f"[get_merchant_ledgers] Merchant not found — merchant_id={merchant_id}")
        raise IncorrectMerchant()

    qs = Ledger.objects.filter(merchant=merchant).order_by("-id")

    if cursor:
        qs = qs.filter(id__lt=cursor)

    ledger = list(qs[:page_size + 1]) 

    has_next = len(ledger) > page_size
    if has_next:
        ledger = ledger[:page_size]

    return {
        "results": ledger,
        "next_cursor": str(ledger[-1].id) if has_next and ledger else None,
        "has_next": has_next,
    }

def get_held_balance(merchant_id: str) -> int:
    result = Payout.objects.filter(
        merchant_id=merchant_id,
        status__in=['pending', 'processing']
    ).aggregate(
        balance=Coalesce(Sum('amount_paise'), Value(0))
    )
    
    return result['balance']
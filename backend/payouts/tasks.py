from celery import shared_task
from django.utils import timezone
import random
from django.db import transaction
from .constants import (
    STATUS_PENDING,
    STATUS_PROCESSING,
    STATUS_COMPLETED,
    STATUS_FAILED,
    OUTCOME_SUCCESS,
    OUTCOME_FAILURE,
    OUTCOME_HANG
)

@shared_task
def process_payout(payout_id: str):
    from .models import Payout
    from ledger.models import Ledger
    
    try:
        payout = Payout.objects.get(id=payout_id)
    except Payout.DoesNotExist:
        return
    
    if payout.status != STATUS_PENDING:
        return
    
    payout.status = STATUS_PROCESSING
    payout.attempts += 1
    payout.last_attempted_at = timezone.now()
    payout.save()
    
    outcome = random.choices(
        [OUTCOME_SUCCESS, OUTCOME_FAILURE, OUTCOME_HANG],
        weights=[70, 20, 10],
    )[0]
    
    if outcome == OUTCOME_SUCCESS:
        with transaction.atomic():
            payout = Payout.objects.select_for_update().get(id=payout_id)
            payout.status = "completed"
            payout.save()
    elif outcome == OUTCOME_FAILURE:
        with transaction.atomic():
            payout = Payout.objects.select_for_update().get(id=payout_id)
            payout.status = "failed"
            payout.failure_reason = "Transaction failed"
            payout.save()
            
            # refund the amount to the merchant
            Ledger.objects.create(
                merchant=payout.merchant,
                entry_type='credit',
                amount_paise=payout.amount_paise,
                description=f'Refund for failed transaction - {payout.id}',
                payout=payout
            )

@shared_task
def retry_timeout_payouts():
    from .models import Payout
    from ledger.models import Ledger
    
    timeout_threshold = timezone.now() - timezone.timedelta(seconds=30)
    
    stuck_payouts = Payout.objects.filter(
        status=STATUS_PROCESSING,
        last_attempted_at=timeout_threshold
    )
    
    for payout in stuck_payouts:
        if payout.attempts < 3:
            process_payout.delay(str(payout.id)) # type: ignore[attr-defined]
        else:
            with transaction.atomic():
                payout = Payout.objects.select_for_update().get(id=payout.id)
                
                if payout.status != STATUS_PROCESSING:
                    continue
                
                payout.status = STATUS_FAILED
                payout.failure_reason = "Max retries exceeded"
                payout.save()
                
                # refund the amount to the merchant
                Ledger.objects.create(
                    merchant=payout.merchant,
                    entry_type='credit',
                    amount_paise=payout.amount_paise,
                    description=f'Refund for max retries exceeded - {payout.id}',
                    payout=payout
                )
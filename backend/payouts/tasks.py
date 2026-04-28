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
import logging

logger = logging.getLogger(__name__)

@shared_task()
def process_payout(payout_id: str):
    from .models import Payout
    from ledger.models import Ledger
    
    logger.info(f"[process_payout] Starting payout_id={payout_id}")

    with transaction.atomic():
        payout = Payout.objects.select_for_update().get(id=payout_id)

        if payout.status != STATUS_PENDING:
            logger.warning(f"[process_payout] Skipping payout_id={payout_id} — status is '{payout.status}', expected PENDING")
            return
        payout.transition_to(STATUS_PROCESSING)
        payout.attempts += 1
        payout.last_attempted_at = timezone.now()
        payout.save(update_fields=['status', 'attempts', 'last_attempted_at', 'updated_at'])
        logger.info(f"[process_payout] payout_id={payout_id} → PROCESSING (attempt {payout.attempts})")

    
    outcome = random.choices(
        [OUTCOME_SUCCESS, OUTCOME_FAILURE, OUTCOME_HANG],
        weights=[70, 20, 10],
    )[0]

    logger.info(f"[process_payout] payout_id={payout_id} outcome={outcome} attempt={payout.attempts}")

    
    if outcome == OUTCOME_SUCCESS:
        with transaction.atomic():
            payout = Payout.objects.select_for_update().get(id=payout_id)
            payout.transition_to(STATUS_COMPLETED)
            payout.save(update_fields=['status', 'updated_at'])
            logger.info(f"[process_payout] payout_id={payout_id} → COMPLETED ✅")
    elif outcome == OUTCOME_FAILURE:
        with transaction.atomic():
            payout = Payout.objects.select_for_update().get(id=payout_id)
            payout.transition_to(STATUS_FAILED)
            payout.failure_reason = "Transaction failed"
            payout.save(update_fields=['status', 'failure_reason', 'updated_at'])
            logger.info(f"[process_payout] payout_id={payout_id} → FAILED ❌")

            # refund the amount to the merchant
            Ledger.objects.create(
                merchant=payout.merchant,
                entry_type='credit',
                amount_paise=payout.amount_paise,
                description=f'Refund for failed transaction - {payout.id}',
                payout=payout
            )
        
        logger.info(f"[process_payout] payout_id={payout_id} refunded ✅")
    elif outcome == OUTCOME_HANG:
        logger.info(f"[process_payout] payout_id={payout_id} → HANG ⏳")
        
    logger.info(f"[process_payout] payout_id={payout_id} → completed with outcome={outcome}")


@shared_task()
def retry_timeout_payouts():
    from .models import Payout
    from ledger.models import Ledger

    BASE_TIMEOUT_SECONDS = 30

    min_threshold = timezone.now() - timezone.timedelta(seconds=BASE_TIMEOUT_SECONDS)
    payouts = Payout.objects.filter(
        status=STATUS_PROCESSING,
        last_attempted_at__lte=min_threshold,
    )

    count = payouts.count()
    logger.info(f"[retry_timeout_payouts] Found {count} candidate payout(s) stuck in PROCESSING")

    if count == 0:
        return

    now = timezone.now()

    for payout in payouts:
        backoff_seconds = BASE_TIMEOUT_SECONDS * (2 ** (payout.attempts - 1))
        payout_timeout = timezone.timedelta(seconds=backoff_seconds)
        time_stuck = (now - payout.last_attempted_at).total_seconds() if payout.last_attempted_at is not None else None

        logger.info(f"[retry_timeout_payouts] payout_id={payout.id} attempts={payout.attempts} stuck={time_stuck:.1f}s required={backoff_seconds}s")

        if payout.last_attempted_at and (now - payout.last_attempted_at) < payout_timeout:
            logger.info(f"[retry_timeout_payouts] payout_id={payout.id} → skipping, {time_stuck:.1f}s < {backoff_seconds}s backoff window")
            continue

        if payout.attempts < 3:
            with transaction.atomic():
                p = Payout.objects.select_for_update().get(id=payout.id)
                if p.status != STATUS_PROCESSING:
                    logger.warning(f"[retry_timeout_payouts] payout_id={payout.id} — status changed to '{p.status}' under lock, skipping")
                    continue
                p.transition_to(STATUS_PENDING)
                p.save(update_fields=['status', 'updated_at'])
                payout_id = str(p.id)
                transaction.on_commit(lambda pid=payout_id: process_payout.delay(pid))  # type: ignore[attr-defined]
                logger.info(f"[retry_timeout_payouts] payout_id={payout.id} → reset to PENDING for retry ♻️")
        else:
            with transaction.atomic():
                p = Payout.objects.select_for_update().get(id=payout.id)
                if p.status != STATUS_PROCESSING:
                    logger.warning(f"[retry_timeout_payouts] payout_id={payout.id} — status changed to '{p.status}' under lock, skipping")
                    continue
                p.transition_to(STATUS_FAILED)
                p.failure_reason = "Max retries exceeded"
                p.save(update_fields=['status', 'failure_reason', 'updated_at'])

                # refund the amount to the merchant
                Ledger.objects.create(
                    merchant=p.merchant,
                    entry_type='credit',
                    amount_paise=p.amount_paise,
                    description=f'Refund for max retries exceeded - {p.id}',
                    payout=p,
                )
                logger.info(f"[retry_timeout_payouts] payout_id={payout.id} → FAILED (max retries) with refund 💸")
from .models import IdempotencyKey
from merchants.models import Merchant
from typing import Any
import logging

logger = logging.getLogger(__name__)

def get_idempotency_key(key: str, merchant: Merchant) -> IdempotencyKey | None:
    try:
        record = IdempotencyKey.objects.get(key=key, merchant=merchant)
        logger.info(f"[get_idempotency_key] Found key='{key}' merchant_id={merchant.id} in_flight={record.in_flight}")
        return record
    except IdempotencyKey.DoesNotExist:
        return None

def create_idempotency_key(key: str, merchant: Merchant) -> IdempotencyKey:
    record = IdempotencyKey.objects.create(
        key=key, 
        merchant=merchant,
        in_flight=True
    )
    logger.info(f"[create_idempotency_key] Created key='{key}' merchant_id={merchant.id}")
    return record

def update_idempotency_key(
    idempotency_key: IdempotencyKey, 
    response_status: int, 
    response_body: Any
) -> IdempotencyKey:
    idempotency_key.in_flight = False
    idempotency_key.response_status = response_status
    idempotency_key.response_body = response_body
    idempotency_key.save()
    logger.info(f"[update_idempotency_key] Finalized key='{idempotency_key.key}' response_status={response_status}")
    return idempotency_key
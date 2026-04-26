from .models import IdempotencyKey
from merchants.models import Merchant
from typing import Any

def get_idempotency_key(key: str, merchant: Merchant) -> IdempotencyKey | None:
    try:
        return IdempotencyKey.objects.get(key=key, merchant=merchant)
    except IdempotencyKey.DoesNotExist:
        return None

def create_idempotency_key(key: str, merchant: Merchant) -> IdempotencyKey:
    return IdempotencyKey.objects.create(
        key=key, 
        merchant=merchant,
        in_flight=True
    )

def update_idempotency_key(
    idempotency_key: IdempotencyKey, 
    response_status: int, 
    response_body: Any
) -> IdempotencyKey:
    idempotency_key.in_flight = False
    idempotency_key.response_status = response_status
    idempotency_key.response_body = response_body
    idempotency_key.save()
    return idempotency_key
# EXPLAINER.md

## 1. The Ledger

### Balance Calculation Query

```python
# ledger/services.py — get_available_balance()
result = Ledger.objects.filter(
    merchant_id=merchant_id
).aggregate(
    balance=Coalesce(
        Sum(
            Case(
                When(entry_type='credit', then=F('amount_paise')),
                When(entry_type='debit', then=-F('amount_paise')),
                default=Value(0),
                output_field=BigIntegerField()
            )
        ),
        Value(0)
    )
)
```

This translates to a single SQL `SELECT SUM(CASE WHEN ... THEN amount_paise WHEN ... THEN -amount_paise END) FROM ledgers WHERE merchant_id = %s`. The balance is never stored — it is always derived from the ledger entries at the database level.

### Why this model?

Credits and debits are separate rows in a single `ledgers` table with an `entry_type` discriminator (`credit` or `debit`). Each row is immutable — once created, it is never updated or deleted.

I chose this over a cached balance column because:

- **Auditability.** Every INR that enters or leaves a merchant's account has a corresponding ledger row. You can reconstruct the balance at any point in time by summing entries up to that timestamp.
- **No drift.** A cached `balance` field can desync from reality if any write path forgets to update it. With a derived balance, the invariant `SUM(credits) - SUM(debits) = displayed balance` holds by construction.
- **Atomic refunds.** When a payout fails, the refund is a new credit row created inside the same `transaction.atomic()` block as the status change. There is no separate "update balance" step that could fail independently.

Amounts are `BigIntegerField` in paise (1 INR = 100 paise). No floats, no decimals. Integer arithmetic has no rounding issues.

---

## 2. The Lock

### The exact code

```python
# payouts/services.py — create_payout()
with transaction.atomic():
    # Lock the merchant row — serializes all concurrent payout requests for this merchant
    merchant = Merchant.objects.select_for_update().get(id=bank_account.merchant.id)

    # ... idempotency check ...

    # Balance check runs INSIDE the locked transaction
    balance = get_available_balance(merchant_id=str(merchant.id))
    if balance < amount_paise:
        raise InSufficientFunds()

    # Create payout + debit entry
    payout = Payout.objects.create(...)
    Ledger.objects.create(entry_type='debit', ...)
```

### What database primitive it relies on

PostgreSQL's `SELECT ... FOR UPDATE` — a **pessimistic locking** strategy. When a transaction acquires this lock on a row, all other transactions that attempt to access the same row are **blocked** until the lock is released (i.e., the holding transaction commits or rolls back). This is the right choice for a payment system where correctness matters more than throughput — we assume conflicts will happen and prevent them upfront, rather than detecting them after the fact.

This means: if two concurrent requests both try to create a ₹60 payout for a merchant with ₹100 balance, the first request acquires the lock, checks the balance (₹100 ≥ ₹60 ✅), creates the debit, and commits. The second request was blocked on `select_for_update()`, and when it finally acquires the lock, it re-reads the balance (now ₹40 < ₹60 ❌) and raises `InSufficientFunds`.

The lock is on the `merchants` row, not on ledger rows. This is intentional — locking a single row is cheaper than locking all ledger entries, and it guarantees that the balance check + debit write happen atomically with respect to other payout requests for the same merchant.

---

## 3. The Idempotency

### How the system knows it has seen a key before

The `idempotency_keys` table has a `UniqueConstraint` on `(key, merchant)`:

```python
# idempotencykey/models.py
class IdempotencyKey(models.Model):
    key = models.CharField(max_length=255)
    merchant = models.ForeignKey(Merchant, on_delete=models.PROTECT)
    in_flight = models.BooleanField(default=True)
    response_status = models.IntegerField(null=True)
    response_body = models.JSONField(null=True)
    created_at = models.GeneratedField(...)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['key', 'merchant'],
                name='unique_idempotency_key_per_merchant'
            ),
        ]
```

On every payout request, the service looks up the key:

1. **Key not found** → create a new record with `in_flight=True`, proceed with payout creation.
2. **Key found, < 24h old, `in_flight=False`** → return the cached `response_body`. No new payout.
3. **Key found, < 24h old, `in_flight=True`** → the first request is still processing. Return `409 Conflict`.
4. **Key found, ≥ 24h old** → expired. Delete the old record, treat as a new key.

After the payout is successfully created, the idempotency record is updated: `in_flight=False`, `response_status=202`, `response_body={serialized payout}`.

### What happens if the first request is in flight when the second arrives

The `in_flight` boolean field handles this. When the first request creates the idempotency key record, it sets `in_flight=True`. If a second request arrives with the same key while the first is still inside the `transaction.atomic()` block:

- If the first transaction has committed but the response hasn't been sent yet: the second request finds `in_flight=False` and returns the cached response. Correct.
- If the first transaction is still in-flight: the second request finds `in_flight=True` and raises `ConflictIdempotencyKey`, returning a `409`. The client should retry after a short delay.

Both cases prevent duplicate payouts.

---

## 4. The State Machine

### Where is `failed → completed` blocked?

```python
# payouts/models.py

VALID_TRANSITIONS: dict[str, set[str]] = {
    STATUS_PENDING:    {STATUS_PROCESSING},
    STATUS_PROCESSING: {STATUS_COMPLETED, STATUS_FAILED, STATUS_PENDING},
    STATUS_COMPLETED:  set(),  # no transitions allowed
    STATUS_FAILED:     set(),  # no transitions allowed
}

class Payout(models.Model):
    # ...
    def transition_to(self, new_status: str):
        allowed = VALID_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise InvalidStateTransition(
                f"Cannot transition from '{self.status}' to '{new_status}'"
            )
        self.status = new_status
```

`STATUS_FAILED` maps to an empty set. Calling `payout.transition_to('completed')` on a failed payout will raise `InvalidStateTransition` because `'completed'` is not in `set()`.

Every status change in the codebase goes through `transition_to()`. There are no direct `payout.status = X` assignments. The legal lifecycle is:

```
pending → processing → completed     (happy path)
pending → processing → failed        (bank rejected / max retries)
processing → pending                 (retry after timeout)
```

`completed` and `failed` are terminal. No backward transitions are possible.

---

## 5. The AI Audit

### Bug 1: `select_for_update(skip_locked=True)` on a targeted `.get()`

When I asked AI to write the payout processing task, it used `skip_locked=True`:

```python
# What AI generated (wrong)
payout = Payout.objects.select_for_update(skip_locked=True).get(id=payout_id)
```

I asked AI whether using `skip_locked` here was okay, and it said yes. But while thinking deeper about it, I realized that in a payment system, consistency is the first priority. `skip_locked=True` tells Postgres to exclude locked rows from the result set. If the payout row is locked by another transaction (e.g., the retry worker), the queryset returns zero rows, and `.get()` raises `Payout.DoesNotExist`. The Celery task crashes silently, and the payout is never processed — the funds remain held forever.

To gain atomicity, I have to block the transaction so the current worker waits until the lock is released. Only then should another worker be able to pick up that payout. `skip_locked` is designed for worker-pool patterns (`SELECT ... FOR UPDATE SKIP LOCKED LIMIT 1`), not for targeting a specific row by primary key.

```python
# What I replaced it with
payout = Payout.objects.select_for_update().get(id=payout_id)
```

This is the kind of bug that passes all tests (tests rarely have two transactions racing on the same row) but fails in production under Celery concurrency.

### Bug 2: Trying to lock inside an aggregate query

My initial approach for the balance check during payout creation was to lock the ledger rows directly:

```python
# What I initially tried (wrong)
result = Ledger.objects.filter(
    merchant_id=merchant_id
).select_for_update().aggregate(
    balance=Coalesce(Sum(Case(...)), Value(0))
)
```

The idea was to lock all ledger rows for this merchant while calculating the balance, preventing concurrent payouts from reading stale data. But `select_for_update()` with `.aggregate()` does not actually lock rows — PostgreSQL does not apply `FOR UPDATE` on aggregate queries because there are no individual rows to return and lock.

I realized I needed a different approach: lock a single shared resource that all payout requests for the same merchant must go through. The merchant row itself is the natural choice:

```python
# What I replaced it with
merchant = Merchant.objects.select_for_update().get(id=bank_account.merchant.id)

# Now the balance check runs inside the locked transaction — safe
balance = get_available_balance(merchant_id=str(merchant.id))
```

By locking the merchant row with `SELECT FOR UPDATE`, all concurrent payout requests for the same merchant are serialized. The balance check + debit write happen atomically because no other transaction can proceed until the lock is released. This is cheaper than locking ledger rows (one row lock vs. many) and actually works with aggregation.

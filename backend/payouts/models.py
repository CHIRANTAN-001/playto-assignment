from django.db import models
from django.db.models import CheckConstraint, Q, F
from common.db.functions import UUIDv7, UUIDExtractTimestamp
from merchants.models import Merchant, BankAccount
from .constants import (
    STATUS_PENDING,
    STATUS_PROCESSING,
    STATUS_COMPLETED,
    STATUS_FAILED
)


class InvalidStateTransition(Exception):
    """Raised when a payout status transition violates the state machine."""
    pass


# Legal state transitions for the payout lifecycle:
#   pending -> processing -> completed    (happy path)
#   pending -> processing -> failed      (bank rejected)
#   processing -> pending               (retry after timeout)
# Terminal states (completed, failed) allow NO outgoing transitions.
VALID_TRANSITIONS: dict[str, set[str]] = {
    STATUS_PENDING:    {STATUS_PROCESSING},
    STATUS_PROCESSING: {STATUS_COMPLETED, STATUS_FAILED, STATUS_PENDING},
    STATUS_COMPLETED:  set(),  # no transitions allowed
    STATUS_FAILED:     set(),  # no transitions allowed
}


class Payout(models.Model):
    STATUS_CHOICES = (
        (STATUS_PENDING, STATUS_PENDING),
        (STATUS_PROCESSING, STATUS_PROCESSING),
        (STATUS_COMPLETED, STATUS_COMPLETED),
        (STATUS_FAILED, STATUS_FAILED)
    )
    
    id=models.UUIDField(
        primary_key=True, 
        db_default=UUIDv7(output_field=models.UUIDField()), 
        editable=False
    )
    merchant=models.ForeignKey(Merchant, on_delete=models.PROTECT)
    amount_paise=models.BigIntegerField()
    bank_account=models.ForeignKey(BankAccount, on_delete=models.PROTECT)
    
    status=models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    
    attempts=models.IntegerField(default=0)
    
    last_attempted_at=models.DateTimeField(null=True, blank=True)
    
    failure_reason=models.CharField(max_length=255, null=True, blank=True)
    task_id=models.CharField(max_length=255, null=True, blank=True)
    
    created_at=models.GeneratedField(
        expression=UUIDExtractTimestamp("id"),
        output_field=models.DateTimeField(),
        db_persist=True
    )
    updated_at=models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "payouts"
        indexes = [
            # for retry worker query
            models.Index(fields=['status', 'last_attempted_at'])
        ]
        constraints  = [
            CheckConstraint(
                condition=models.Q(amount_paise__gt=0),
                name="payouts_amount_paise_positive"
            ),
            CheckConstraint(
                condition=Q(attempts__lte=3),
                name="payouts_max_attempts"
            )
        ]
    
    def transition_to(self, new_status: str):
        allowed = VALID_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise InvalidStateTransition(
                f"Cannot transition from '{self.status}' to '{new_status}'"
            )
        self.status = new_status

    def __str__(self):
        return f"{self.merchant} - {self.amount_paise} - {self.status} - {self.attempts}"
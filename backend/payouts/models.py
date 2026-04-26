from django.db import models
from django.db.models import CheckConstraint, Q, F
from common.db.functions import UUIDv7, UUIDExtractTimestamp
from merchants.models import Merchant, BankAccount



# Create your views here.
class Payout(models.Model):
    STATUS_CHOICES = (
        ("pending", "pending"),
        ("processing", "processing"),
        ("completed", "completed"),
        ("failed", "failed")
    )
    
    id=models.UUIDField(
        primary_key=True, 
        db_default=UUIDv7(output_field=models.UUIDField()), 
        editable=False
    )
    merchant=models.ForeignKey(Merchant, on_delete=models.PROTECT)
    amount_paise=models.BigIntegerField()
    bank_account=models.ForeignKey(BankAccount, on_delete=models.PROTECT)
    
    status=models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    
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
    
    def __str__(self):
        return f"{self.merchant} - {self.amount_paise} - {self.status} - {self.attempts}"
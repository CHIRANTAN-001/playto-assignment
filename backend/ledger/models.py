from django.db import models
from common.db.functions import UUIDv7, UUIDExtractTimestamp
from merchants.models import Merchant
from payouts.models import Payout

# Create your models here.
class Ledger(models.Model):
    id=models.UUIDField(
        primary_key=True,
        db_default=UUIDv7(output_field=models.UUIDField()),
        editable=False
    )
    merchant=models.ForeignKey(Merchant, on_delete=models.PROTECT, db_index=False)
    
    ENTRY_TYPES= (
        ("credit", "credit"),
        ("debit", "debit")
    )
    
    entry_type=models.CharField(max_length=10, choices=ENTRY_TYPES)
    # value of amount_praise is greater than equal to 0
    amount_paise=models.BigIntegerField()
    description=models.CharField(max_length=255)
    payout=models.ForeignKey(Payout, on_delete=models.PROTECT, null=True, blank=True)
    created_at=models.GeneratedField(
        expression=UUIDExtractTimestamp("id"),
        output_field=models.DateTimeField(),
        db_persist=True
    )
    
    class Meta:
        db_table = "ledgers"
        indexes = [
            models.Index(fields=["merchant", "created_at"])
        ]
    
    def __str__(self) -> str:
        return f"{self.entry_type} - {self.amount_paise} - {self.description}"
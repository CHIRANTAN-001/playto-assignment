from django.db import models
from common.db.functions import UUIDv7, UUIDExtractTimestamp
from merchants.models import Merchant

# Create your models here.
class IdempotencyKey(models.Model):
    id=models.UUIDField(
        primary_key=True,
        db_default=UUIDv7(output_field=models.UUIDField()),
        editable=False
    )
    key=models.CharField(max_length=255)
    merchant=models.ForeignKey(Merchant, on_delete=models.PROTECT)
    in_flight=models.BooleanField(default=True)
    response_status=models.IntegerField(null=True, blank=True)
    response_body=models.JSONField(null=True, blank=True)
    created_at=models.GeneratedField(
        expression=UUIDExtractTimestamp("id"),
        output_field=models.DateTimeField(),
        db_persist=True
    )
    
    class Meta:
        db_table = 'idempotency_keys'
        constraints = [
            models.UniqueConstraint(
                fields=['key', 'merchant'], 
                name='unique_idempotency_key_per_merchant'
            ),
        ]
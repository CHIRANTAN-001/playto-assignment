from django.db import models
from common.db.functions import UUIDv7, UUIDExtractTimestamp

# Create your models here.

class Merchant(models.Model):
    id=models.UUIDField(
        primary_key=True, 
        db_default=UUIDv7(output_field=models.UUIDField()), 
        editable=False
    )
    name=models.CharField(max_length=50)
    email=models.EmailField(null=False)
    created_at=models.GeneratedField(
        expression=UUIDExtractTimestamp("id"),
        output_field=models.DateTimeField(),
        db_persist=True
    )
    
    class Meta:
        db_table = "merchants"
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                name="merchants_email_unique",
            )
        ]
    
    def __str__(self):
        return f"{self.name} - {self.email}"


class BankAccount(models.Model):
    id=models.UUIDField(
        primary_key=True,
        db_default=UUIDv7(output_field=models.UUIDField()),
        editable=False
    )
    merchant=models.ForeignKey(
        Merchant, 
        on_delete=models.CASCADE,
        related_name="bank_accounts"
    )
    account_number = models.CharField(max_length=20)
    created_at=models.GeneratedField(
        expression=UUIDExtractTimestamp("id"),
        output_field=models.DateTimeField(),
        db_persist=True
    )
    
    class Meta:
        db_table = "bank_accounts"
        constraints = [
            models.UniqueConstraint(
                fields=["account_number"],
                name="bank_accounts_account_number_unique",
            )
        ]
    
    def __str__(self) -> str:
        return f"{self.account_number} - {self.merchant}"
    
    
    
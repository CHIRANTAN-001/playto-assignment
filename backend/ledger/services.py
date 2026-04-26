from .models import Ledger
from merchants.models import Merchant
from django.db.models import Sum, Case, When, F, Value, BigIntegerField
from django.db.models.functions import Coalesce
from uuid import UUID

def create_credit_entry(merchant: Merchant, amount_paise: int) -> Ledger:
    return Ledger.objects.create(
        merchant=merchant,
        entry_type='credit',
        amount_paise=amount_paise,
        description='Initial credit - seed data'
    )

# check balance
def get_available_balance(merchant_id: str) -> int:
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
    
    return result['balance']

# check balance with lock - only used during transaction
def get_available_balance_for_update(merchant_id: UUID) -> int:
    result = Ledger.objects.filter(
        merchant_id=merchant_id
    ).select_for_update().aggregate(
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
    
    return result['balance']
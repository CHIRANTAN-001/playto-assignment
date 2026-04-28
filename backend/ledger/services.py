from .models import Ledger
from merchants.models import Merchant
from django.db.models import Sum, Case, When, F, Value, BigIntegerField
from django.db.models.functions import Coalesce
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

def create_credit_entry(merchant: Merchant, amount_paise: int) -> Ledger:
    entry = Ledger.objects.create(
        merchant=merchant,
        entry_type='credit',
        amount_paise=amount_paise,
        description='Initial credit - seed data'
    )
    logger.info(f"[create_credit_entry] merchant_id={merchant.id} amount_paise={amount_paise}")
    return entry

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
    
    balance = result['balance']
    logger.debug(f"[get_available_balance] merchant_id={merchant_id} balance={balance}")
    return balance

# check balance with lock - only used during transaction (Previously used this code but later removed it coz aggregation with select_for_update() is not possible. Now done manually)
# def get_available_balance_for_update(merchant_id: UUID) -> int:
#     result = Ledger.objects.filter(
#         merchant_id=merchant_id
#     ).select_for_update().aggregate(
#         balance=Coalesce(
#             Sum(
#                 Case(
#                     When(entry_type='credit', then=F('amount_paise')),
#                     When(entry_type='debit', then=-F('amount_paise')),
#                     default=Value(0),
#                     output_field=BigIntegerField()
#                 )
#             ),
#             Value(0)
#         )
#     )
    
#     balance = result['balance']
#     logger.debug(f"[get_available_balance_for_update] merchant_id={merchant_id} balance={balance} (locked)")
#     return balance

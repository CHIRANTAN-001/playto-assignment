from .models import Ledger
from merchants.models import Merchant

def create_credit_entry(merchant: Merchant, amount_paise: int) -> Ledger:
    return Ledger.objects.create(
        merchant=merchant,
        entry_type='credit',
        amount_paise=amount_paise,
        description='Initial credit - seed data'
    )
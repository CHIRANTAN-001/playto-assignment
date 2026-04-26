from django.core.management.base import BaseCommand
from django.db import transaction
from merchants.services import create_merchant, create_bank_account
from ledger.services import create_credit_entry
from merchants.models import Merchant, BankAccount
from ledger.models import Ledger

SEED_DATA = [
    {
        "merchant": {
            "name": "John Doe",
            "email": "john.doe@example.com"
        },
        "bank": {
            "account_number": "1234567890"
        },
        "credits": [
            {
                "amount_paise": 100000 * 100,  # ₹100000
            },
            {
                "amount_paise": 250000 * 100,  # ₹250000
            },
        ]
    },
    {
        "merchant": {
            "name": "Jane Doe",
            "email": "jane.doe@example.com"
        },
        "bank": {
            "account_number": "9876543210"
        },
        "credits": [
            {
                "amount_paise": 500000 * 100,  # ₹500000
            },
            {
                "amount_paise": 150000 * 100,  # ₹150000
            },
        ]
    },
]

class Command(BaseCommand):
    help = 'Seed merchants with bank accounts and credit history'
    def handle(self, *args, **kwargs):
        # create 2 - 3 merchants
        for data in SEED_DATA:
            with transaction.atomic():
                # check if the merchant already exists
                if Merchant.objects.filter(email=data['merchant']['email']).exists():
                    self.stdout.write(f"Skipping {data['merchant']['email']} as it already exists.")
                    continue
                
                # call the service layer
                merchant = create_merchant(**data['merchant'])
                
                # create bank account for each
                create_bank_account(merchant=merchant, **data['bank'])
                
                # create credit ledger entries (simulate customer payments)
                for credit in data['credits']:
                    create_credit_entry(
                        merchant=merchant,
                        amount_paise=credit['amount_paise'],
                    )
                
                self.stdout.write(self.style.SUCCESS(
                    f"Merchant {data['merchant']['email']} created successfully with "
                    f"INR: {sum(c['amount_paise'] for c in data['credits']) // 100}"
                ))
from django.core.management.base import BaseCommand
from django.db import transaction
from merchants.services import create_merchant, create_bank_account
from ledger.services import create_credit_entry
from merchants.models import Merchant, BankAccount
from django.core.exceptions import ValidationError


SEED_DATA = [
    {
        "merchant": {
            "name": "John Doe",
            "email": "john.doe@example.com"
        },
        "banks": [
            {"account_number": "1234567890"},
            {"account_number": "1234567891"},
        ],
        "credits": [
            {"amount_paise": 100000 * 100},
            {"amount_paise": 250000 * 100},
        ]
    },
    {
        "merchant": {
            "name": "Jane Doe",
            "email": "jane.doe@example.com"
        },
        "banks": [
            {"account_number": "9876543210"},
            {"account_number": "9876543211"},
        ],
        "credits": [
            {"amount_paise": 500000 * 100},
            {"amount_paise": 150000 * 100},
        ]
    },
]

class Command(BaseCommand):
    help = "Seed merchants with multiple bank accounts and credit history"

    def handle(self, *args, **kwargs):
        for data in SEED_DATA:
            with transaction.atomic():
                email = data["merchant"]["email"]

                # Get or create merchant (idempotent)
                merchant, created = Merchant.objects.get_or_create(
                    email=email,
                    defaults={"name": data["merchant"]["name"]},
                )

                if created:
                    self.stdout.write(f"Created merchant: {email}")
                else:
                    self.stdout.write(f"Merchant {email} already exists, syncing...")

                # Create bank accounts that don't exist yet
                accounts_created = 0
                for bank in data["banks"]:
                    acct_num = bank["account_number"]
                    if not BankAccount.objects.filter(account_number=acct_num).exists():
                        create_bank_account(
                            merchant=merchant,
                            account_number=acct_num,
                        )
                        accounts_created += 1

                # Only create credits for brand-new merchants
                total_amount = 0
                if created:
                    for credit in data["credits"]:
                        create_credit_entry(
                            merchant=merchant,
                            amount_paise=credit["amount_paise"],
                        )
                        total_amount += credit["amount_paise"]

                bank_count = BankAccount.objects.filter(merchant=merchant).count()
                self.stdout.write(self.style.SUCCESS(
                    f"✅ {email} | "
                    f"Accounts: {bank_count} ({accounts_created} new) | "
                    f"Credits added: ₹{total_amount // 100}"
                ))
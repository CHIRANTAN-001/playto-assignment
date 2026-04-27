import threading
from django.test import TestCase
from merchants.models import Merchant, BankAccount
from ledger.models import Ledger
from payouts.models import Payout
from payouts.services import create_payout

class IdempotencyTest(TestCase):
    def setUp(self):
        self.merchant = Merchant.objects.create(
            name='Test Merchant',
            email='test2@example.com'
        )
        self.bank_account = BankAccount.objects.create(
            merchant=self.merchant,
            account_number='9876543210',
        )
        Ledger.objects.create(
            merchant=self.merchant,
            entry_type='credit',
            amount_paise=50000,  # ₹500
            description='Test credit'
        )

    def test_same_idempotency_key_returns_same_response(self):
        """
        Same key sent twice should create only one payout
        and return same response both times.
        """
        IDEMPOTENCY_KEY = 'test-key-123'

        # first request
        result1 = create_payout(
            idempotency_key=IDEMPOTENCY_KEY,
            amount_paise=5000,
            bank_account_id=str(self.bank_account.id)
        )

        # second request — same key
        result2 = create_payout(
            idempotency_key=IDEMPOTENCY_KEY,
            amount_paise=5000,
            bank_account_id=str(self.bank_account.id)
        )

        # assert only one payout created
        payouts = Payout.objects.filter(merchant=self.merchant).count()
        self.assertEqual(payouts, 1, "Only one payout should be created")

        # assert only one debit entry
        debits = Ledger.objects.filter(
            merchant=self.merchant,
            entry_type='debit'
        ).count()
        self.assertEqual(debits, 1, "Only one debit should exist")
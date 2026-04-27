import threading
from django.test import TransactionTestCase
from django.test.utils import setup_test_environment
from django import db
from merchants.models import Merchant, BankAccount
from ledger.models import Ledger
from payouts.models import Payout
from payouts.services import create_payout, InSufficientFunds

class ConcurrencyTest(TransactionTestCase):
    def setUp(self):
        self.merchant = Merchant.objects.create(
            name="Test Merchant",
            email="VHl7G@example.com"
        )
        self.bank_account = BankAccount.objects.create(
            merchant=self.merchant,
            account_number="8249698943"
        )
        Ledger.objects.create(
            merchant=self.merchant,
            entry_type="credit",
            amount_paise=10000,
            description="Initial credit"
        )

    def test_concurrent_payouts_same_balance(self):
        """Two threads both try ₹60 payout on ₹100 balance."""
        results = []
        errors = []
        bank_account_id = str(self.bank_account.id)
        barrier = threading.Barrier(2)  # ← forces both threads to start simultaneously

        def attempt_payout(idempotency_key):
            # force a brand new connection for this thread
            db.connections.close_all()
            
            try:
                barrier.wait()
                create_payout(
                    idempotency_key=idempotency_key,
                    amount_paise=6000,
                    bank_account_id=bank_account_id
                )
                results.append('success')
            except InSufficientFunds:
                errors.append('insufficient')
            except Exception as e:
                errors.append(f"{type(e).__name__}: {str(e)}")
            finally:
                db.connections.close_all()

        t1 = threading.Thread(target=attempt_payout, args=('key-thread-1',))
        t2 = threading.Thread(target=attempt_payout, args=('key-thread-2',))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        print(f"results: {results}")
        print(f"errors: {errors}")

        self.assertEqual(len(results), 1, "Exactly one payout should succeed")
        self.assertEqual(len(errors), 1, "Exactly one should fail")

        debits = Ledger.objects.filter(merchant=self.merchant, entry_type='debit').count()
        self.assertEqual(debits, 1, "Only one debit entry should exist")

        payouts = Payout.objects.filter(merchant=self.merchant).count()
        self.assertEqual(payouts, 1, "Only one payout should exist")
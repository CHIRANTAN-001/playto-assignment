from django.urls import path
from .views import MerchantBalanceView, MerchantPayoutListView, MerchantLedgerListView, MerchantBankAccountView, MerchantLookupView

urlpatterns = [
    path("<uuid:id>/balance/", MerchantBalanceView.as_view()),
    path("<uuid:id>/payouts/", MerchantPayoutListView.as_view()),
    path("<uuid:id>/ledger/", MerchantLedgerListView.as_view()),
    path("<uuid:id>/bank-accounts/", MerchantBankAccountView.as_view()),
    path("login/", MerchantLookupView.as_view())
]

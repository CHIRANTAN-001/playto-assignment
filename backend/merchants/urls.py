from django.urls import path
from .views import MerchantBalanceView, MerchantPayoutView

urlpatterns = [
    path('<uuid:id>/balance/', MerchantBalanceView.as_view()),
    path('<uuid:id>/payouts/', MerchantPayoutView.as_view()),
]
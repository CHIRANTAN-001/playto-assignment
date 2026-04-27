from django.urls import path
from .views import PayoutView, MerchantPayoutView

urlpatterns = [
    path('', PayoutView.as_view()),
    path('<uuid:payout_id>/', MerchantPayoutView.as_view())
]
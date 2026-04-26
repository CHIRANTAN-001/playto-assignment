from django.urls import path
from .views import MerchantBalanceView

urlpatterns = [
    path('<uuid:id>/balance/', MerchantBalanceView.as_view()),
]
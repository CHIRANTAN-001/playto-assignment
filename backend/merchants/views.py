from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from .models import Merchant
from ledger.services import get_available_balance
from utils.response import api_response, api_error
from payouts import serializer as payout_serializer, services as payout_services

# Create your views here.
class MerchantBalanceView(APIView):
    def get(self, request: Request, id):
        # check mer chant exsists
        try:
            merchant= Merchant.objects.get(id=id)
        except Merchant.DoesNotExist:
            return api_error(status_code=status.HTTP_404_NOT_FOUND)
        
        balance = get_available_balance(merchant_id=id)
        
        response = {
            "merchant_id": str(merchant.id),
            "merchant_name": merchant.name,
            "balance_paise": balance,
            "balance_inr": balance // 100
        }
        
        return api_response(data=response, message="Balance fetched successfully", status_code=status.HTTP_200_OK)

class MerchantPayoutView(APIView):
    def get(self, request: Request, id):
        response = payout_services.get_payout(payout_id=id)
        if not response:
            return api_error(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Payout not found"
            )
        serializer = payout_serializer.PayoutResponseSerializer(response).data
        return api_response(
            data=serializer,
            message="Payout fetched successfully",
            status_code=status.HTTP_200_OK
        )
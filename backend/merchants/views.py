from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from .models import Merchant
from ledger.services import get_available_balance
from utils.response import api_response, api_error
from payouts import serializer as payout_serializer, services as payout_services
from ledger import serializer as ledger_serializer
from payouts.services import IncorrectMerchant, get_held_balance
from .serializer import BankAccountSerializer, MerchantLookupSerializer, MerchantSerializer
import logging

logger = logging.getLogger(__name__)

# Create your views here.
class MerchantBalanceView(APIView):
    def get(self, request: Request, id):
        try:
            merchant = Merchant.objects.get(id=id)
        except Merchant.DoesNotExist:
            logger.warning(f"[MerchantBalanceView.get] Merchant not found — merchant_id={id}")
            return api_error(status_code=status.HTTP_404_NOT_FOUND, message="Merchant not found")
        
        available = get_available_balance(merchant_id=id)
        held = get_held_balance(merchant_id=id)
        
        response = {
            "merchant_id": str(merchant.id),
            "merchant_name": merchant.name,
            "balance": {
                "available_paise": available,
                "available_inr": available / 100,
                "held_paise": held,
                "held_inr": held / 100,
                "total_paise": available + held,
                "total_inr": (available + held) / 100,
            }
        }
        
        return api_response(data=response, message="Balance fetched successfully", status_code=status.HTTP_200_OK)
    
class MerchantPayoutListView(APIView):
    def get(self, request: Request, id):
        cursor = request.query_params.get("cursor")
        page_size = int(request.query_params.get("page_size", 20))
        try:
            response = payout_services.get_merchant_payouts(merchant_id=id, cursor=cursor, page_size=page_size)
        except IncorrectMerchant:
            logger.warning(f"[MerchantPayoutListView.get] Merchant not found — merchant_id={id}")
            return api_error(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Merchant not found"
            )
        
        serialized_data = payout_serializer.PayoutResponseSerializer(response["results"], many=True).data # type: ignore[arg-type]
        response = {
            "results": serialized_data,
            "next_cursor": response["next_cursor"], # type: ignore[arg-type]
            "has_next": response["has_next"] # type: ignore[arg-type]
        }
        return api_response(
            data=response,
            message="Payouts fetched successfully",
        )        

class MerchantLedgerListView(APIView):
    def get(self, request: Request, id):
        cursor = request.query_params.get("cursor")
        page_size = int(request.query_params.get("page_size", 20))
        try:
            response = payout_services.get_merchant_ledgers(merchant_id=id, cursor=cursor, page_size=page_size)
        except IncorrectMerchant:
            logger.warning(f"[MerchantLedgerListView.get] Merchant not found — merchant_id={id}")
            return api_error(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Merchant not found"
            )
        
        serialized_data = ledger_serializer.LedgerResponseSerializer(response["results"], many=True).data # type: ignore[arg-type]
        response = {
            "results": serialized_data,
            "next_cursor": response["next_cursor"], # type: ignore[arg-type]
            "has_next": response["has_next"] # type: ignore[arg-type]
        }
        return api_response(
            data=response,
            message="Payouts fetched successfully",
        )       

class MerchantBankAccountView(APIView):
    def get(self, request: Request, id):
        try:
            merchant = Merchant.objects.get(id=id)
        except Merchant.DoesNotExist:
            logger.warning(f"[MerchantBankAccountView.get] Merchant not found — merchant_id={id}")
            return api_error(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Merchant not found"
            )
        accounts = merchant.bank_accounts.all() # pyright: ignore[reportAttributeAccessIssue]
        serialized_data = BankAccountSerializer(accounts, many=True).data
        
        return api_response(
            data=serialized_data,
            message="Banl account fetched successfully"
        )

class MerchantLookupView(APIView):
    def post(self, request: Request):
        serializer = MerchantLookupSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"[MerchantLookupView.post] Validation failed — errors={serializer.errors}")
            return api_error(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Merchant not found",
                data=serializer.errors
            )
        
        data = serializer.data

        try:
            email=""
            if isinstance(data, dict) and "email" in data:
                email = data["email"]
            merchant = Merchant.objects.get(email=email)
        except Merchant.DoesNotExist:
            logger.warning(f"[MerchantLookupView.post] Merchant not found — email={email}")
            return api_error(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Merchant not found"
            )
        
        logger.info(f"[MerchantLookupView.post] Merchant found — merchant_id={merchant.id} email={email}")
        response_serializer = MerchantSerializer(instance=merchant)

        return api_response(
            data=response_serializer.data,
            message="Merchant fetched successfully"
        )
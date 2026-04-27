from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.request import Request
from .models import Payout
from .serializer import PayoutRequestSerializer, PayoutResponseSerializer
from idempotencykey.services import get_idempotency_key
from utils.response import api_error, api_response
from rest_framework import status
from .services import create_payout, get_payout
from .services import InSufficientFunds, ConflictIdempotencyKey, InvalidBankAccount

# Create your views here.
class PayoutView(APIView):
    def post(self, request: Request):
        # 1. get idempotency key
        idempotency_key = request.headers.get("Idempotency-Key")
        
        if not idempotency_key:
            return api_error(
                status_code=status.HTTP_400_BAD_REQUEST, 
                message="Idempotency key is required"
            )
        
        # 2. validate request body
        serializer = PayoutRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return api_error(
                status_code=status.HTTP_400_BAD_REQUEST, 
                message="Invalid request body",
                data=serializer.errors
            )
        payload = serializer.validated_data
        
        # 3. create payout
        try:
            payout = create_payout(
                idempotency_key=idempotency_key,
                amount_paise=payload["amount_paise"], # type: ignore
                bank_account_id=str(payload["bank_account_id"]) # type: ignore
            )       
        except InvalidBankAccount:
            return api_error(
                status_code=status.HTTP_400_BAD_REQUEST, 
                message="Invalid bank account"
            )
        except InSufficientFunds:
            return api_error(
                status_code=status.HTTP_400_BAD_REQUEST, 
                message="Insufficient funds"
            )
        except ConflictIdempotencyKey:
            return api_error(
                status_code=status.HTTP_409_CONFLICT, 
                message="Idempotency key already exists"
            )
        except Exception as e:
            return api_error(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                message=str(e)
            )
        
        return api_response(
            data=PayoutResponseSerializer(payout).data, 
            message="Payout created successfully",
            status_code=status.HTTP_202_ACCEPTED
        )


class MerchantPayoutView(APIView):
    def get(self, request: Request, payout_id):
        response = get_payout(payout_id=payout_id)
        if not response:
            return api_error(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Payout not found"
            )
        serializer = PayoutResponseSerializer(response).data
        return api_response(
            data=serializer,
            message="Payout fetched successfully",
            status_code=status.HTTP_200_OK
        )

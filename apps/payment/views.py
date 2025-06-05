from decouple import config
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TicketTransaction
from .serializer import TicketTransactionSerializer
from .service import TransactionRequest, send_payment_request, verify_payment_request
from .utils import CurrencyEnum

MERCHANT_ID = config("MERCHANT_ID")
DEFAULT_CURRENCY = CurrencyEnum.IRT


class PayTransactionView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketTransactionSerializer

    def post(self, request, bill_id):
        bill = get_object_or_404(TicketTransaction, id=bill_id, paid_by=request.user)

        ta_req = TransactionRequest(
            merchant_id=MERCHANT_ID,
            amount=int(bill.amount),
            currency=DEFAULT_CURRENCY,
            callback_url=settings.CALLBACK_URL,
        )
        response = send_payment_request(ta_req)

        if response["status"] == 200:
            bill.authority = response["authority"]
            bill.save()
            return redirect(response["response"])
        else:
            return Response(response, status=400)


class VerifyPaymentView(APIView):
    serializer_class = TicketTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, authority):
        ticket_transaction = get_object_or_404(TicketTransaction, authority=authority)
        response = verify_payment_request(authority, ticket_transaction.amount, MERCHANT_ID)

        if response["status"] == 100:
            ticket_transaction.confirm(response["ref_id"])
            return Response({"message": "Payment verified", "ref_id": response["ref_id"]})
        else:
            return Response(response, status=400)

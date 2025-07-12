from decouple import config
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .choices import CurrencyChoice, BillStatusChoice
from .models import TicketTransaction
from .serializer import TicketTransactionSerializer
from .service import TransactionRequest, send_payment_request, verify_payment_request

MERCHANT_ID = config("MERCHANT_ID")
DEFAULT_CURRENCY = CurrencyChoice.IRT


class PayTransactionView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketTransactionSerializer

    def post(self, request, transaction):
        bill = TicketTransaction.objects.filter(
            public_id=transaction,
            tickets__user=request.user,
            status=BillStatusChoice.PENDING.name
        ).distinct().get()

        ta_req = TransactionRequest(
            merchant_id=MERCHANT_ID,
            amount=int(bill.amount),
            currency=DEFAULT_CURRENCY,
            description="Test Description",
            callback_url=settings.CALLBACK_URL,
        )
        response = send_payment_request(ta_req)

        if response["status"]:
            bill.authority = response["authority"]
            bill.save()
            return Response(response,status=200)
        else:
            return Response(response, status=400)


class VerifyPaymentView(APIView):
    serializer_class = TicketTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, authority):
        ticket_transaction = TicketTransaction.objects.filter(
            authority=authority,
            tickets__user=request.user,
            status=BillStatusChoice.PENDING.name
        ).distinct().get()

        response = verify_payment_request(authority, ticket_transaction.amount, MERCHANT_ID)

        if response["status"]:
            ref_id = response["data"]["ref_id"]
            ticket_transaction.confirm(ref_id)
            return Response({"message": "Payment verified", "ref_id": ref_id})
        else:
            return Response(response, status=400)

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
BASE_AMOUNT = 1000 # if amount is lesser than base amount it will automatically confirm the transaction
DEFAULT_CURRENCY = CurrencyChoice.IRT


class PayTransactionView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketTransactionSerializer

    def post(self, request, transaction):
        ticket_transaction = TicketTransaction.objects.filter(
            public_id=transaction,
            tickets__user=request.user,
            status=BillStatusChoice.PENDING.value
        ).distinct()

        ticket_transaction = get_object_or_404(ticket_transaction)

        if ticket_transaction.amount < BASE_AMOUNT:
            ticket_transaction.status = BillStatusChoice.SUCCESS.value
            ticket_transaction.authority = ticket_transaction.public_id
            ticket_transaction.save()
            return Response({"message": "Payment verified", "authority": ticket_transaction.public_id})
        else:
            ta_req = TransactionRequest(
                merchant_id=MERCHANT_ID,
                amount=int(ticket_transaction.amount),
                currency=DEFAULT_CURRENCY,
                description="Test Description",
                callback_url=settings.CALLBACK_URL,
            )
            response = send_payment_request(ta_req)

            if response["status"]:
                ticket_transaction.authority = response["authority"]
                ticket_transaction.save()
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
        ).distinct()

        ticket_transaction = get_object_or_404(ticket_transaction)
        ref_id = ticket_transaction.transaction_id

        match BillStatusChoice(ticket_transaction.status):
            case BillStatusChoice.CANCELLED:
                return Response({"message": "transaction canceled"}, status=400)
            case BillStatusChoice.PENDING:
                response = verify_payment_request(authority, ticket_transaction.amount, MERCHANT_ID)
                if response["status"]:
                    ref_id = response["data"]["ref_id"]
                    ticket_transaction.confirm(ref_id)
                else:
                    return Response(response, status=400)

            case BillStatusChoice.SUCCESS: ...

        ref_id = ticket_transaction.transaction_id
        return Response({"message": "Payment verified", "ref_id": ref_id})

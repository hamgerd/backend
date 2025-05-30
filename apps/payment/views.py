from rest_framework import permissions,status
from django.shortcuts import get_object_or_404, redirect
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.conf import LazySettings, settings
from utils import CurrencyEnum
from decouple import config


from .models import TicketTransaction, BillStatus
from .serializer import TicketTransactionSerializer
from .service import verify_payment_request ,send_payment_request, TransactionRequest, Metadata

MERCHANT_ID = config("MERCHANT_ID")

# @api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
# def get_bill(request, bill_id):
#     bill = get_object_or_404(TicketTransaction, id=bill_id, paid_by=request.user)
#     serializer = TicketTransactionSerializer(bill)
#     return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def pay_bill(request, bill_id):
    bill = get_object_or_404(TicketTransaction, id=bill_id, paid_by=request.user)
    ta_req = TransactionRequest(
        merchant_id=MERCHANT_ID,
        amount=int(bill.amount),  # Assumes amount in cents or cast to int as required
        currency=CurrencyEnum(bill.currency),
        description=bill.description,
        callback_url=settings.CALLBACK_URL,
    )
    response = send_payment_request(ta_req, settings)

    if response["status"] == 200:
        bill.authority = response["authority"]
        redirect(response["response"])
    else:
        return response



@api_view(['POST'])
def verify_payment(request, authority):
    ticket_transaction = get_object_or_404(TicketTransaction, authority=authority)
    response = verify_payment_request(authority, ticket_transaction.amount, settings)
    if response["status"] == 100:
        ticket_transaction.status = BillStatus.CONFIRMED
        ticket_transaction.transaction_id = response['ref_id']
    else:
        return response

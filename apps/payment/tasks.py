from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import BillStatusChoice, TicketTransaction


@shared_task
def invalidate_transactions():
    unpaid_tickets_list = TicketTransaction.objects.filter(
        status=BillStatusChoice.PENDING.value, created_at__lt=timezone.now() - timedelta(minutes=15)
    )

    for transaction in unpaid_tickets_list:
        transaction.cancel()

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from ...payment.models import TicketTransaction
from ...payment.utils import BillStatus
from ...users.models import User
from ..models import Event, Ticket
from ..utils import TicketStatus


def create_transaction_for_tickets(event: Event, user: User):
    """
    1) Fetch all Ticket rows for the given (event, user) that DO NOT yet have a transaction.
    2) Sum their final_amount.
    3) Create one TicketTransaction with that amount.
    4) Associate all those tickets to that new transaction in bulk.
    5) Return the newly created TicketTransaction.
    """

    tickets_qs = Ticket.objects.filter(
        ticket_type__event=event, user=user, transaction__isnull=True, status=TicketStatus.PENDING.value
    )

    if not tickets_qs.exists():
        return None

    total_amount = tickets_qs.aggregate(total=Sum("final_amount"))["total"] or 0

    with transaction.atomic():
        new_tx = TicketTransaction.objects.create(amount=total_amount)
        tickets_qs.update(transaction=new_tx)

    return new_tx


def confirm_transaction(tx: TicketTransaction, gateway_transaction_id: str) -> TicketTransaction:
    """
    Confirms a TicketTransaction and all associated tickets:
    - Set transaction.status = PAID
    - Set transaction.transaction_id = gateway_transaction_id
    - Set paid_at = now
    - Set all related Ticket.status = CONFIRMED
    """
    with transaction.atomic():
        # Update the transaction itself
        tx.status = BillStatus.CONFIRMED.name
        tx.transaction_id = gateway_transaction_id
        tx.paid_at = timezone.now()
        tx.save(update_fields=["status", "transaction_id", "paid_at"])

        # Update all related tickets
        tx.tickets.update(status=TicketStatus.CONFIRMED.value)

    return tx

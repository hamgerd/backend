from django.db.models import Sum

from apps.events.choices import CommissionPayerChoice, EventStatusChoice
from apps.events.models import Event, Ticket
from apps.payment.choices import AccountingServiceTypeChoice, BalanceTypeChoice
from apps.payment.models import OrganizationAccounting


def finalize_event(event: Event):
    """
    Finalizes the event by:
      - Setting the event status to "COMPLETED".
      - Calculating total ticket income and commission.
      - Creating a credit accounting record for the event's income.
      - If the seller pays the commission, also creates a debit accounting record for the commission amount.
    """
    event.status = EventStatusChoice.COMPLETED.value
    event.save()
    tickets_summary = Ticket.objects.filter(ticket_type__event=event).aggregate(
        total_amount=Sum("final_amount"), total_commission=Sum("commission")
    )

    event_income = tickets_summary["total_amount"] or 0
    event_commission = tickets_summary["total_commission"] or 0

    OrganizationAccounting.objects.create(
        amount=event_income,
        service=AccountingServiceTypeChoice.EVENT_PAYMENT,
        organization=event.organization,
        balance=BalanceTypeChoice.CREDIT,
        extra_arguments={"description": "event income"},
    )
    if event.commission_payer == CommissionPayerChoice.SELLER:
        OrganizationAccounting.objects.create(
            amount=event_commission,
            service=AccountingServiceTypeChoice.EVENT_PAYMENT,
            organization=event.organization,
            balance=BalanceTypeChoice.DEBIT,
            extra_arguments={"description": "event commission"},
        )

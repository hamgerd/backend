import pytest

from apps.core.exceptions import BadRequestException
from apps.events.choices import CommissionPayerChoice, EventStatusChoice
from apps.payment.choices import BalanceTypeChoice
from apps.payment.models import OrganizationAccounting


class TestEventModel:
    def test_finalize_event_raises_exception_when_event_is_not_over(self, event):
        with pytest.raises(BadRequestException, match="Event is not over yet."):
            event.finalize_event()

    def test_finalize_event_raises_exception_when_event_is_already_completed(self, event):
        event.status = EventStatusChoice.COMPLETED
        event.save()

        with pytest.raises(BadRequestException, match="Event is already completed."):
            event.finalize_event()

    def test_finalize_event_creates_no_commission_when_commission_payer_is_the_buyer(self, event, ticket_type):
        event.commission_payer = CommissionPayerChoice.BUYER
        event.save()

        event.finalize_event()

        assert (
            OrganizationAccounting.objects.filter(
                balance=BalanceTypeChoice.DEBIT,
                organization=event.organization,
                extra_arguments__description="event commission",
            ).exists()
            is False
        )

    def test_finalize_event_creates_no_commission_when_no_commission_is_gathered(self, event, ticket_type, ticket):
        ticket.commission = 0
        ticket.save()

        event.finalize_event()

        assert (
            OrganizationAccounting.objects.filter(
                balance=BalanceTypeChoice.DEBIT,
                organization=event.organization,
                extra_arguments__description="event commission",
            ).exists()
            is False
        )

    def test_finalize_event_creates_a_commission_when_commission_is_gathered_on_a_single_ticket(
        self, event, ticket_type, create_ticket, another_user
    ):
        ticket_commission = 1000
        create_ticket(user=another_user, ticket_type=ticket_type, commission=ticket_commission)

        event.finalize_event()

        commissions = OrganizationAccounting.objects.filter(
            balance=BalanceTypeChoice.DEBIT,
            organization=event.organization,
            extra_arguments__description="event commission",
        )
        assert commissions.count() == 1
        assert commissions[0].amount == ticket_commission

    def test_finalize_event_creates_a_commission_when_commission_is_gathered_on_multiple_tickets_with_same_type(
        self, event, ticket_type, create_ticket, another_user
    ):
        ticket_commission = 1000
        create_ticket(user=another_user, ticket_type=ticket_type, commission=ticket_commission)
        create_ticket(user=another_user, ticket_type=ticket_type, commission=ticket_commission)
        create_ticket(user=another_user, ticket_type=ticket_type, commission=ticket_commission)

        event.finalize_event()

        commissions = OrganizationAccounting.objects.filter(
            balance=BalanceTypeChoice.DEBIT,
            organization=event.organization,
            extra_arguments__description="event commission",
        )
        assert commissions.count() == 1
        assert commissions[0].amount == 3 * ticket_commission

    def test_finalize_event_creates_a_commission_when_commission_is_gathered_on_multiple_tickets_multiple_same_types(
        self, event, create_ticket_type, create_ticket, another_user
    ):
        first_ticket_type = create_ticket_type(max_participants=10, event=event, price=10000)
        second_ticket_type = create_ticket_type(max_participants=20, event=event, price=20000)
        first_ticket_commission = 1000
        second_ticket_commission = 2000
        create_ticket(user=another_user, ticket_type=first_ticket_type, commission=first_ticket_commission)
        create_ticket(user=another_user, ticket_type=first_ticket_type, commission=first_ticket_commission)
        create_ticket(user=another_user, ticket_type=second_ticket_type, commission=second_ticket_commission)
        create_ticket(user=another_user, ticket_type=second_ticket_type, commission=second_ticket_commission)

        event.finalize_event()

        commissions = OrganizationAccounting.objects.filter(
            balance=BalanceTypeChoice.DEBIT,
            organization=event.organization,
            extra_arguments__description="event commission",
        )
        assert commissions.count() == 1
        assert commissions[0].amount == 2 * first_ticket_commission + 2 * second_ticket_commission

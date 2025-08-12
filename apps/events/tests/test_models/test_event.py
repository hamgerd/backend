from datetime import timedelta

import pytest
import time_machine
from django.utils import timezone
from rest_framework.exceptions import NotAcceptable, ValidationError

from apps.events.choices import CommissionPayerChoice, EventStatusChoice
from apps.events.services.event import finalize_event
from apps.payment.choices import BalanceTypeChoice
from apps.payment.models import OrganizationAccounting


class TestEventModel:
    def test_finalize_event_raises_exception_when_event_is_not_over(self, event):
        with pytest.raises(NotAcceptable, match="Event is not over yet."):
            finalize_event(event)

    def test_finalize_event_raises_exception_when_event_is_already_completed(self, event):
        event.status = EventStatusChoice.COMPLETED
        event.save()

        after_event_time = event.end_date + timedelta(hours=1)
        with time_machine.travel(after_event_time):
            with pytest.raises(NotAcceptable, match="Event is already completed."):
                finalize_event(event)

    def test_finalize_event_creates_no_commission_when_commission_payer_is_the_buyer(self, event, ticket_type):
        event.commission_payer = CommissionPayerChoice.BUYER
        event.save()

        after_event_time = event.end_date + timedelta(hours=1)
        with time_machine.travel(after_event_time):
            finalize_event(event)

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

        after_event_time = event.end_date + timedelta(hours=1)
        with time_machine.travel(after_event_time):
            finalize_event(event)

        event_commission_exists = OrganizationAccounting.objects.filter(
            balance=BalanceTypeChoice.DEBIT,
            organization=event.organization,
            extra_arguments__description="event commission",
        ).exists()
        assert event_commission_exists is False

    def test_finalize_event_creates_a_commission_when_commission_is_gathered_on_a_single_ticket(
        self, event, ticket_type, create_ticket, another_user
    ):
        ticket_commission = 1000
        create_ticket(user=another_user, ticket_type=ticket_type, commission=ticket_commission)

        after_event_time = event.end_date + timedelta(hours=1)
        with time_machine.travel(after_event_time):
            finalize_event(event)

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

        after_event_time = event.end_date + timedelta(hours=1)
        with time_machine.travel(after_event_time):
            finalize_event(event)

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

        after_event_time = event.end_date + timedelta(hours=1)
        with time_machine.travel(after_event_time):
            finalize_event(event)

        commissions = OrganizationAccounting.objects.filter(
            balance=BalanceTypeChoice.DEBIT,
            organization=event.organization,
            extra_arguments__description="event commission",
        )
        assert commissions.count() == 1
        assert commissions[0].amount == 2 * first_ticket_commission + 2 * second_ticket_commission

    def test_create_event_with_registration_opening_after_start_date_fails(self, create_event, organization):
        start_date = timezone.now() + timedelta(days=7)
        end_date = timezone.now() + timedelta(days=8)
        registration_opening = start_date + timedelta(hours=1)
        with pytest.raises(ValidationError, match="Registration opening must be before the event start date."):
            create_event(
                organization=organization,
                start_date=start_date,
                end_date=end_date,
                registration_opening=registration_opening,
            )

    def test_create_event_with_registration_deadline_after_end_date_date_fails(self, create_event, organization):
        start_date = timezone.now() + timedelta(days=7)
        end_date = timezone.now() + timedelta(days=8)
        registration_deadline = end_date + timedelta(hours=1)
        with pytest.raises(ValidationError):
            create_event(
                organization=organization,
                start_date=start_date,
                end_date=end_date,
                registration_deadline=registration_deadline,
            )

    def test_update_end_date_fails_after_event_status_is_completed(self, event):
        event.status = EventStatusChoice.COMPLETED
        event.save()

        with pytest.raises(NotAcceptable, match="Event is already completed."):
            event.end_date = timezone.now() + timedelta(days=1)
            event.save()

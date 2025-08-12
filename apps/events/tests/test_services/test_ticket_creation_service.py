import uuid
from datetime import timedelta

import pytest
import time_machine
from rest_framework.exceptions import ValidationError

from apps.core.exceptions import BadRequestException
from apps.events.choices import CommissionPayerChoice, EventStatusChoice, TicketStatusChoice
from apps.events.models import Ticket
from apps.events.services.tickets import TicketCreationService
from apps.payment.choices import BillStatusChoice, CommissionActionTypeChoice
from apps.payment.models import TicketTransaction
from apps.payment.tasks import invalidate_transactions


class TestTicketCreationService:
    def test_create_ticket_fails_if_event_end_date_is_reached(self, ticket_type, event, another_user):
        ticket_types = [{"ticket_type_public_id": ticket_type.public_id, "count": 1}]

        after_event_time = event.end_date + timedelta(hours=1)
        with time_machine.travel(after_event_time):
            with pytest.raises(BadRequestException, match="Event is not open to register."):
                TicketCreationService().handle_ticket_creation(
                    event=event, user=another_user, ticket_types=ticket_types
                )

    def test_create_ticket_fails_if_event_registration_deadline_is_reached(self, ticket_type, event, another_user):
        event.registration_deadline = event.end_date - timedelta(hours=2)
        ticket_types = [{"ticket_type_public_id": ticket_type.public_id, "count": 1}]

        after_event_time = event.end_date - timedelta(hours=1)
        with time_machine.travel(after_event_time):
            with pytest.raises(BadRequestException, match="Event is not open to register."):
                TicketCreationService().handle_ticket_creation(
                    event=event, user=another_user, ticket_types=ticket_types
                )

    def test_create_ticket_fails_if_event_status_not_equal_to_scheduled(self, ticket_type, event, another_user):
        event.status = EventStatusChoice.DRAFT
        event.save()
        ticket_types = [{"ticket_type_public_id": ticket_type.public_id, "count": 1}]

        with pytest.raises(BadRequestException, match="Event is not open to register."):
            TicketCreationService().handle_ticket_creation(event=event, user=another_user, ticket_types=ticket_types)

    def test_tickets_released_after_timeout_when_unpaid_by_user(self, ticket_type, event, another_user):
        ticket_types = [{"ticket_type_public_id": ticket_type.public_id, "count": 1}]

        TicketCreationService().handle_ticket_creation(event=event, user=another_user, ticket_types=ticket_types)

        assert Ticket.objects.first().status == TicketStatusChoice.PENDING
        assert TicketTransaction.objects.first().status == BillStatusChoice.PENDING

        after_expiration = timedelta(minutes=16)
        with time_machine.travel(after_expiration):
            invalidate_transactions()

        assert Ticket.objects.first().status == TicketStatusChoice.CANCELLED
        assert TicketTransaction.objects.first().status == BillStatusChoice.CANCELLED

    def test_create_ticket_fails_if_non_existing_ticket_type_public_id_is_passed(self, event, another_user):
        ticket_types = [{"ticket_type_public_id": uuid.uuid4(), "count": 1}]

        with pytest.raises(ValidationError, match="Wrong ticket type is sent."):
            TicketCreationService().handle_ticket_creation(event=event, user=another_user, ticket_types=ticket_types)

    def test_create_ticket_fails_if_no_tickets_are_available(self, ticket_type, event, another_user):
        first_ticket_types = [{"ticket_type_public_id": ticket_type.public_id, "count": ticket_type.max_participants}]
        second_ticket_types = [{"ticket_type_public_id": ticket_type.public_id, "count": 1}]

        TicketCreationService().handle_ticket_creation(event=event, user=another_user, ticket_types=first_ticket_types)

        with pytest.raises(ValidationError, match=f"No ticket is available for {ticket_type.public_id} ticket type"):
            TicketCreationService().handle_ticket_creation(
                event=event, user=another_user, ticket_types=second_ticket_types
            )

    def test_create_ticket_fails_if_not_enough_tickets_are_available(self, ticket_type, event, another_user):
        ticket_types = [{"ticket_type_public_id": ticket_type.public_id, "count": ticket_type.max_participants + 1}]

        with pytest.raises(
            ValidationError,
            match=f"Only {ticket_type.max_participants} ticket is remaining for {ticket_type.public_id} ticket type",
        ):
            TicketCreationService().handle_ticket_creation(event=event, user=another_user, ticket_types=ticket_types)

    def test_create_single_non_free_ticket_with_commission_payer_set_to_buyer(
        self, ticket_type, event, another_user, create_commission_rule
    ):
        ticket_type_commission = create_commission_rule(
            ticket_type.price - 100, ticket_type.price + 100, CommissionActionTypeChoice.CONSTANT, 100
        )
        event.commission_payer = CommissionPayerChoice.BUYER
        event.save()
        ticket_types = [{"ticket_type_public_id": ticket_type.public_id, "count": 1}]

        TicketCreationService().handle_ticket_creation(event=event, user=another_user, ticket_types=ticket_types)
        ticket = Ticket.objects.first()
        transaction = TicketTransaction.objects.first()

        assert Ticket.objects.count() == 1
        assert ticket.commission == 100
        assert ticket.final_amount == ticket_type.price
        assert TicketTransaction.objects.count() == 1
        assert transaction.amount == ticket_type.price + ticket_type_commission.amount

    def test_create_single_non_free_ticket_with_no_commission_rule(self, ticket_type, event, another_user):
        ticket_types = [{"ticket_type_public_id": ticket_type.public_id, "count": 1}]

        TicketCreationService().handle_ticket_creation(event=event, user=another_user, ticket_types=ticket_types)
        ticket = Ticket.objects.first()
        transaction = TicketTransaction.objects.first()

        assert Ticket.objects.count() == 1
        assert ticket.commission == 0
        assert ticket.final_amount == ticket_type.price
        assert TicketTransaction.objects.count() == 1
        assert transaction.amount == ticket_type.price

    def test_create_two_non_free_tickets_of_same_type_with_no_commission_rule(self, ticket_type, event, another_user):
        ticket_types = [{"ticket_type_public_id": ticket_type.public_id, "count": 2}]

        TicketCreationService().handle_ticket_creation(event=event, user=another_user, ticket_types=ticket_types)
        ticket = Ticket.objects.first()
        transaction = TicketTransaction.objects.first()

        assert Ticket.objects.count() == 2
        assert ticket.commission == 0
        assert ticket.final_amount == ticket_type.price
        assert TicketTransaction.objects.count() == 1
        assert transaction.amount == ticket_type.price * 2

    def test_create_two_non_free_tickets_of_different_types_with_no_commission_rule(
        self, create_ticket_type, event, another_user
    ):
        first_ticket_type = create_ticket_type(10, event, 10000)
        second_ticket_type = create_ticket_type(5, event, 20000)
        ticket_types = [
            {"ticket_type_public_id": first_ticket_type.public_id, "count": 1},
            {"ticket_type_public_id": second_ticket_type.public_id, "count": 1},
        ]

        TicketCreationService().handle_ticket_creation(event=event, user=another_user, ticket_types=ticket_types)
        first_ticket_type_tickets = Ticket.objects.filter(ticket_type=first_ticket_type)
        second_ticket_type_tickets = Ticket.objects.filter(ticket_type=second_ticket_type)
        transaction = TicketTransaction.objects.first()

        assert Ticket.objects.count() == 2
        assert first_ticket_type_tickets.count() == 1
        assert second_ticket_type_tickets.count() == 1
        assert first_ticket_type_tickets[0].commission == 0
        assert second_ticket_type_tickets[0].commission == 0
        assert first_ticket_type_tickets[0].final_amount == first_ticket_type.price
        assert second_ticket_type_tickets[0].final_amount == second_ticket_type.price
        assert TicketTransaction.objects.count() == 1
        assert transaction.amount == first_ticket_type.price + second_ticket_type.price

    def test_create_two_non_free_tickets_of_different_types_with_commission_rules(
        self, create_ticket_type, event, another_user, create_commission_rule
    ):
        first_ticket_type = create_ticket_type(10, event, 10000)
        second_ticket_type = create_ticket_type(5, event, 20000)
        first_ticket_type_commission = create_commission_rule(
            first_ticket_type.price - 100, first_ticket_type.price + 100, CommissionActionTypeChoice.CONSTANT, 100
        )
        second_ticket_type_commission = create_commission_rule(
            second_ticket_type.price - 100, second_ticket_type.price + 100, CommissionActionTypeChoice.CONSTANT, 200
        )
        ticket_types = [
            {"ticket_type_public_id": first_ticket_type.public_id, "count": 2},
            {"ticket_type_public_id": second_ticket_type.public_id, "count": 2},
        ]

        TicketCreationService().handle_ticket_creation(event=event, user=another_user, ticket_types=ticket_types)
        first_ticket_type_tickets = Ticket.objects.filter(ticket_type=first_ticket_type)
        second_ticket_type_tickets = Ticket.objects.filter(ticket_type=second_ticket_type)
        transaction = TicketTransaction.objects.first()

        assert Ticket.objects.count() == 4
        assert first_ticket_type_tickets.count() == 2
        assert second_ticket_type_tickets.count() == 2
        assert first_ticket_type_tickets[0].commission == first_ticket_type_commission.amount
        assert second_ticket_type_tickets[0].commission == second_ticket_type_commission.amount
        assert first_ticket_type_tickets[0].final_amount == first_ticket_type.price
        assert second_ticket_type_tickets[0].final_amount == second_ticket_type.price
        assert TicketTransaction.objects.count() == 1
        assert transaction.amount == (first_ticket_type.price + second_ticket_type.price) * 2

    def test_create_single_free_ticket(self, create_ticket_type, event, another_user):
        ticket_type = create_ticket_type(10, event, 0)
        ticket_types = [
            {"ticket_type_public_id": ticket_type.public_id, "count": 1},
        ]

        TicketCreationService().handle_ticket_creation(event=event, user=another_user, ticket_types=ticket_types)
        ticket_type_tickets = Ticket.objects.filter(ticket_type=ticket_type)
        transaction = TicketTransaction.objects.first()

        assert Ticket.objects.count() == 1
        assert ticket_type_tickets.count() == 1
        assert ticket_type_tickets[0].commission == 0
        assert ticket_type_tickets[0].final_amount == 0
        assert TicketTransaction.objects.count() == 1
        assert transaction.amount == 0

    def test_create_single_non_free_ticket_and_single_free_ticket_with_commission_rules(
        self, create_ticket_type, event, another_user, create_commission_rule
    ):
        first_ticket_type = create_ticket_type(10, event, 0)
        second_ticket_type = create_ticket_type(5, event, 20000)
        second_ticket_type_commission = create_commission_rule(
            second_ticket_type.price - 100, second_ticket_type.price + 100, CommissionActionTypeChoice.CONSTANT, 200
        )
        ticket_types = [
            {"ticket_type_public_id": first_ticket_type.public_id, "count": 1},
            {"ticket_type_public_id": second_ticket_type.public_id, "count": 1},
        ]

        TicketCreationService().handle_ticket_creation(event=event, user=another_user, ticket_types=ticket_types)
        first_ticket_type_tickets = Ticket.objects.filter(ticket_type=first_ticket_type)
        second_ticket_type_tickets = Ticket.objects.filter(ticket_type=second_ticket_type)
        transaction = TicketTransaction.objects.first()

        assert Ticket.objects.count() == 2
        assert first_ticket_type_tickets.count() == 1
        assert second_ticket_type_tickets.count() == 1
        assert first_ticket_type_tickets[0].commission == 0
        assert second_ticket_type_tickets[0].commission == second_ticket_type_commission.amount
        assert first_ticket_type_tickets[0].final_amount == 0
        assert second_ticket_type_tickets[0].final_amount == second_ticket_type.price
        assert TicketTransaction.objects.count() == 1
        assert transaction.amount == second_ticket_type.price

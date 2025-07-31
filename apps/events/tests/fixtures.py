from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from faker import Faker

from apps.events.choices import EventStatusChoice
from apps.events.models import Event, Ticket, TicketType
from apps.payment.choices import BillStatusChoice

faker = Faker()


@pytest.fixture
def event(db, organization):
    start_date = timezone.now() + timedelta(days=7)
    end_date = timezone.now() + timedelta(days=7, hours=2)

    return Event.objects.create(
        title=faker.word(),
        description=faker.text(120),
        organization=organization,
        start_date=start_date,
        end_date=end_date,
        status=EventStatusChoice.SCHEDULED,
    )


@pytest.fixture
def create_ticket_type(db):
    def _create_ticket_type(max_participants: int, event: Event, price: int | Decimal):
        return TicketType.objects.create(
            title=faker.word(), max_participants=max_participants, event=event, price=price
        )

    return _create_ticket_type


@pytest.fixture
def ticket_type(db, create_ticket_type, event):
    return create_ticket_type(max_participants=10, event=event, price=10000)


@pytest.fixture
def create_ticket(db, create_transaction):
    def _create_ticket(user, ticket_type, commission, transaction=None):
        if not transaction:
            transaction = create_transaction(
                amount=ticket_type.price, status=BillStatusChoice.SUCCESS, transaction_id=faker.password(length=10)
            )

        return Ticket.objects.create(
            user=user,
            ticket_type=ticket_type,
            final_amount=ticket_type.price,
            commission=commission,
            transaction=transaction,
        )

    return _create_ticket


@pytest.fixture
def ticket(db, another_user, ticket_type, create_ticket):
    return create_ticket(user=another_user, ticket_type=ticket_type, commission=0)

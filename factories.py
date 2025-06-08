# factories.py

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory
from faker import Faker

from apps.events.models import Event, EventCategory, Ticket, TicketStatusChoice, TicketType
from apps.organizations.models import Organization
from apps.users.models import User  # Update this to your actual user model path

fake = Faker()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Faker("company")
    owner = factory.SubFactory(UserFactory)


class EventCategoryFactory(DjangoModelFactory):
    class Meta:
        model = EventCategory

    title = factory.Faker("word")


class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event

    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph", nb_sentences=3)
    organization = factory.SubFactory(OrganizationFactory)
    category = factory.SubFactory(EventCategoryFactory)
    start_date = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(days=1))
    end_date = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(days=2))
    location = factory.Faker("address")
    is_active = True


class TicketTypeFactory(DjangoModelFactory):
    class Meta:
        model = TicketType

    title = factory.Faker("word")
    description = factory.Faker("text")
    max_participants = factory.Faker("random_int", min=1, max=100)
    event = factory.SubFactory(EventFactory)


class TicketFactory(DjangoModelFactory):
    class Meta:
        model = Ticket

    user = factory.SubFactory(UserFactory)
    ticket_type = factory.SubFactory(TicketTypeFactory)
    status = TicketStatusChoice.PENDING.value
    ticket_number = factory.LazyFunction(lambda: fake.uuid4())
    notes = factory.Faker("sentence")

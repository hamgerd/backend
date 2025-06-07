from collections import defaultdict

from django.conf import settings
from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError

from apps.payment.models import TicketTransaction

from ..models import Event, Ticket, TicketType
from ..serializers.ticket import TicketCreateResponseSerializer


class TicketCreationService:
    @classmethod
    @atomic
    def handle_ticket_creation(
        cls, event: Event, user: settings.AUTH_USER_MODEL, ticket_types: list
    ) -> TicketCreateResponseSerializer:
        cls._is_ticket_types_valid(event, ticket_types)
        cls._is_enough_tickets_available(event, ticket_types)

        tickets = cls._create_ticket_objects(user, ticket_types)
        response_tickets_data = cls._get_response_tickets_data(tickets)
        transaction = cls._create_transaction(tickets)

        data = {"transaction_public_id": transaction.public_id, "ticket_data": response_tickets_data}
        serializer = TicketCreateResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer

    @staticmethod
    def _is_ticket_types_valid(event: Event, ticket_types: list):
        """Check if the ticket types belong to the given event"""
        event_ticket_type_ids = event.ticket_types.values_list("public_id", flat=True)
        if not all(ticket_type["ticket_type_public_id"] in event_ticket_type_ids for ticket_type in ticket_types):
            raise ValidationError("Wrong ticket type is sent.")

    @staticmethod
    def _is_enough_tickets_available(event: Event, ticket_types: list):
        requested_types = list(filter(lambda ticket: ticket["count"] > 0, ticket_types))
        public_ids = [type_["ticket_type_public_id"] for type_ in requested_types]
        event_ticket_type_data = event.ticket_types.filter(public_id__in=public_ids, max_participants__isnull=False)
        ticket_type_map = {tt.public_id: tt.remaining_tickets for tt in event_ticket_type_data}
        for ticket_type in requested_types:
            count = ticket_type["count"]
            ticket_type_public_id = ticket_type["ticket_type_public_id"]
            remaining_count = ticket_type_map.get(ticket_type_public_id)

            if remaining_count is not None:
                if remaining_count == 0:
                    raise ValidationError(f"No ticket is available for {ticket_type_public_id} ticket type")
                if count > remaining_count:
                    raise ValidationError(
                        f"Only {remaining_count} ticket is remaining for {ticket_type_public_id} ticket type"
                    )

    @staticmethod
    def _create_ticket_objects(user: settings.AUTH_USER_MODEL, ticket_types: list):
        tickets = []
        for ticket_type in ticket_types:
            if ticket_type["count"] > 0:
                ticket_type_obj = TicketType.objects.get(public_id=ticket_type["ticket_type_public_id"])
                for _ in range(ticket_type["count"]):
                    ticket = Ticket(user=user, ticket_type=ticket_type_obj, final_amount=ticket_type_obj.price)
                    tickets.append(ticket)
        return tickets

    @staticmethod
    def _get_response_tickets_data(tickets: list[Ticket]) -> list:
        """Get the list of ticket_types with ticket public_id list asossiated with them"""
        tickets_by_type = defaultdict(list)
        for ticket in tickets:
            tickets_by_type[ticket.ticket_type.public_id].append(ticket.public_id)
        return [
            {"ticket_type_public_id": ticket_type_id, "ticket_public_ids": ticket_ids}
            for ticket_type_id, ticket_ids in tickets_by_type.items()
        ]

    @staticmethod
    def _create_transaction(tickets: list[Ticket]):
        total_amount = sum(ticket.final_amount for ticket in tickets)
        tx = TicketTransaction.objects.create(amount=total_amount)
        for ticket in tickets:
            ticket.transaction = tx
            ticket.save()
        return tx

from rest_framework import serializers

from ...payment.serializer import TicketTransactionSerializerPublic
from ..models import Ticket, TicketType


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ["public_id", "title", "description", "max_participants", "price"]


class TicketSerializer(serializers.ModelSerializer):
    ticket_type = TicketTypeSerializer(read_only=True)
    transactions = TicketTransactionSerializerPublic(read_only=True, many=False)

    class Meta:
        model = Ticket
        fields = [
            "public_id",
            "ticket_type",
            "status",
            "ticket_number",
            "notes",
            "created_at",
            "updated_at",
            "transactions",
        ]
        read_only_fields = ["public_id", "created_at", "updated_at", "transactions", "status"]


class TicketCreateSerializer(serializers.Serializer):
    ticket_type_public_id = serializers.UUIDField()
    count = serializers.IntegerField(min_value=1)


class TicketsResponseDataSerialize(serializers.Serializer):
    ticket_type_public_id = serializers.UUIDField()
    ticket_public_ids = serializers.ListSerializer(child=serializers.UUIDField(), allow_empty=False)


class TicketCreateResponseSerializer(serializers.Serializer):
    ticket_data = TicketsResponseDataSerialize(many=True, allow_empty=False)
    transaction_public_id = serializers.UUIDField()

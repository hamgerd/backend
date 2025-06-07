from rest_framework import serializers

from .models import TicketTransaction


class TicketTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketTransaction
        fields = [
            "public_id",
            "amount",
            "authority",
            "status",
            "created_at",
            "transaction_id",
            "paid_at",
        ]
        read_only_fields = fields


class TicketTransactionSerializerPublic(serializers.ModelSerializer):
    class Meta:
        model = TicketTransaction
        fields = [
            "public_id",
            "amount",
            "status",
            "created_at",
            "paid_at",
        ]
        read_only_fields = fields

from rest_framework import serializers
from .models import TicketTransaction, Ticket

class TicketTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketTransaction
        fields = [
            'public_id',
            'amount'
            'currency',
            'authority',
            'status',
            'created_at',
            'transaction_id',
            'paid_at',
            "ticket"
        ]
        read_only_fields = fields

class TicketTransactionSerializerPublic(serializers.ModelSerializer):
    class Meta:
        model = TicketTransaction
        fields = [
            'public_id',
            'amount',
            'currency',
            'status',
            'created_at',
            'paid_at',
        ]
        read_only_fields = fields

from rest_framework import serializers
from .models import TicketTransaction, Ticket
from django.contrib.auth import get_user_model

User = get_user_model()

class TicketTransactionSerializer(serializers.ModelSerializer):
    paid_by = serializers.StringRelatedField(read_only=True)
    ticket_id = serializers.PrimaryKeyRelatedField(source='ticket', queryset=Ticket.objects.all(), allow_null=True)

    class Meta:
        model = TicketTransaction
        fields = [
            'id',
            'description',
            'amount',
            'status',
            'paid_by',
            'created_at',
            'paid_at',
            'note',
            'ticket_id',
        ]
        read_only_fields = ['created_at']

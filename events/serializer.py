from rest_framework import serializers

from organization.serializer import OrganizationSerializer

from .models import Event, Ticket, TicketType


class EventSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "organization",
            "start_date",
            "end_date",
            "location",
            "max_participants",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "organization",
            "start_date",
            "end_date",
            "location",
        ]


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ["id", "title", "description", "max_participants"]


class TicketSerializer(serializers.ModelSerializer):
    ticket_type = TicketTypeSerializer(read_only=True)
    event = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ["id", "ticket_type", "status", "ticket_number", "notes", "event", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def get_event(self, obj):
        return {
            "id": obj.ticket_type.event.id,
            "title": obj.ticket_type.event.title,
            "start_date": obj.ticket_type.event.start_date,
            "end_date": obj.ticket_type.event.end_date,
        }


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["ticket_type", "notes"]

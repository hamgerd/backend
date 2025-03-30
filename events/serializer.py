from rest_framework import serializers

from organization.serializer import OrganizationSerializer

from .models import Event


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

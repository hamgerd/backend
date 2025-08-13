from rest_framework import serializers

from apps.core.serializers import GeoLocationSerializer
from apps.organizations.models import Organization
from apps.organizations.serializer import OrganizationSerializer

from ..models import Event, EventCategory, TicketType
from .ticket import TicketTypeSerializer


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ["title"]


class EventSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    ticket_types = TicketTypeSerializer(many=True)
    categories = EventCategorySerializer(many=True)

    class Meta:
        model = Event
        fields = [
            "public_id",
            "title",
            "description",
            "organization",
            "ticket_types",
            "image",
            "categories",
            "status",
            "start_date",
            "end_date",
            "registration_opening",
            "registration_deadline",
            "location",
            "geo_location",
            "max_participants",
            "is_active",
            "commission_payer",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["public_id", "created_at", "updated_at"]


class EventCreateSerializer(serializers.ModelSerializer):
    ticket_types = TicketTypeSerializer(many=True)
    organization = serializers.SlugRelatedField(slug_field="username", queryset=Organization.objects.all())
    categories = serializers.SlugRelatedField(
        slug_field="title", many=True, required=False, queryset=EventCategory.objects.all()
    )
    geo_location = GeoLocationSerializer(required=False, allow_null=True)

    def create(self, validated_data):
        ticket_types_data = validated_data.pop("ticket_types")
        categories_data = validated_data.pop("categories", [])

        categories = EventCategory.objects.filter(title__in=categories_data)
        event = Event.objects.create(**validated_data)

        for ticket_type_data in ticket_types_data:
            TicketType.objects.create(event=event, **ticket_type_data)

        event.categories.set(categories)

        return event

    class Meta:
        model = Event
        fields = [
            "public_id",
            "title",
            "description",
            "organization",
            "image",
            "categories",
            "start_date",
            "end_date",
            "registration_opening",
            "registration_deadline",
            "location",
            "geo_location",
            "ticket_types",
            "commission_payer",
        ]
        read_only_fields = ["public_id"]

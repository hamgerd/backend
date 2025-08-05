from rest_framework import serializers

from apps.core.serializers import GeoLocationSerializer

from .models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "public_id",
            "name",
            "username",
            "logo",
            "description",
            "email",
            "address",
            "website",
            "event_count",
            "geo_location",
        ]
        read_only_fields = ["event_count", "public_id"]


class OrganizationCreateSerializer(serializers.ModelSerializer):
    geo_location = GeoLocationSerializer(required=False, allow_null=True)

    class Meta:
        model = Organization
        fields = ["name", "username", "logo", "description", "email", "address", "website", "geo_location"]

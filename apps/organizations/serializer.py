from rest_framework import serializers

from .models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["public_id", "name", "username", "logo", "description", "email", "address", "website", "event_count"]
        read_only_fields = ["event_count", "public_id"]


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["name", "username", "logo", "description", "email", "address", "website"]

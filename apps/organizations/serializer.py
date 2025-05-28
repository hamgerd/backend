from rest_framework import serializers

from apps.users.serializers.user import UserSerializer

from .models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Organization
        fields = ["id", "name", "description", "email", "owner", "address", "website", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["name", "username", "description", "email", "address", "website"]

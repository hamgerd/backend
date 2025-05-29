from rest_framework import serializers

from apps.users.serializers.user import UserSerializer

from .models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "username", "image", "description", "email", "address", "website"]


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["name", "username", "image", "description", "email", "address", "website"]

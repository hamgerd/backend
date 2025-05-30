from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.organizations.serializer import OrganizationSerializer

USER = get_user_model()


class UserMESerializer(serializers.ModelSerializer):
    organizations = OrganizationSerializer(many=True, read_only=True)

    class Meta:
        model = USER
        fields = ["id", "email", "first_name", "last_name", "image", "organizations"]

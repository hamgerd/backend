from django.contrib.auth import get_user_model
from organization.serializer import OrganizationSerializer
from rest_framework import serializers

USER = get_user_model()

class UserMESerializer(serializers.ModelSerializer):
    organizations = OrganizationSerializer(many=True, read_only=True)

    class Meta:
        model = USER
        fields = ["id", "username", "email", "first_name", "last_name", "organizations"]

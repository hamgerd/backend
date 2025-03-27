from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers

USER = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = USER
        fields = ["id", "username", "email", "first_name", "last_name"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        return USER.objects.create_user(**validated_data, is_active=False)

    class Meta:
        model = USER
        fields = ["username", "email", "password"]

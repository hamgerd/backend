from django.contrib.auth import get_user_model
from rest_framework import serializers

USER = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = USER
        fields = ["id", "username", "email", "first_name", "last_name"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = USER
        fields = ["username", "email", "password"]

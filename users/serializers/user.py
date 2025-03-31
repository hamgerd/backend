from django.contrib.auth import get_user_model
from rest_framework import serializers

USER = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = USER
        fields = ["id", "username", "email", "first_name", "last_name"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return USER.objects.create_user(**validated_data, is_active=False)

    class Meta:
        model = USER
        fields = ["username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="The email address of the user requesting a password reset")

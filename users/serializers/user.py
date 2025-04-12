from django.contrib.auth import get_user_model
from rest_framework import serializers

USER = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = USER
        fields = ["id", "username", "email", "first_name", "last_name", "organizations"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    refresh_token = serializers.CharField(read_only=True)

    def create(self, validated_data):
        return USER.objects.create_user(**validated_data, is_active=False)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["refresh_token"] = self.context.get("refresh_token")
        return representation

    class Meta:
        model = USER
        fields = ["username", "email", "password", "refresh_token"]
        extra_kwargs = {"password": {"write_only": True}}


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="The email address of the user requesting a password reset")


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField(help_text="Password reset token send by email")
    password = serializers.CharField(write_only=True)

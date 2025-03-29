from rest_framework import serializers


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(help_text="The verification token sent to your email")

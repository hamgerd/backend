from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from drf_yasg.openapi import Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from config.settings.base import EMAIL_VERIFICATION_URL, PASSWORD_RESET_URL
from core.tasks.email import send_email
from users.serializers.user import PasswordResetRequestSerializer, UserRegistrationSerializer
from verification.choices import VerificationTypeChoices
from verification.models import VerificationToken

USER = get_user_model()


class UserRegisterView(GenericAPIView):
    """
    Register a new user and send a verification email
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserRegistrationSerializer(),
        responses={
            HTTP_201_CREATED: UserRegistrationSerializer(),
        },
    )
    @transaction.atomic
    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
            valid_for = timedelta(minutes=15)
            verification_token = VerificationToken.objects.create(
                user=user,
                type=VerificationTypeChoices.EMAIL,
                valid_for=valid_for,
            )
            transaction.on_commit(
                lambda: send_email.delay(
                    subject="Verification Email",
                    template_name="users/verification_email.html",
                    from_email=None,
                    recipient_list=[user.email],
                    context={
                        "title": "Verification Email",
                        "token": verification_token.token,
                        "email_verification_url": EMAIL_VERIFICATION_URL,
                    },
                )
            )
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(GenericAPIView):
    """
    Password reset request view
    """

    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            HTTP_201_CREATED: Schema(
                type="object", properties={"message": Schema(type="string", description="Success message")}
            ),
            HTTP_400_BAD_REQUEST: Schema(
                type="object",
                properties={
                    "error": Schema(type="string", description="Error message"),
                    "errors": Schema(
                        type="object",
                        additional_properties=Schema(type="string"),
                    ),
                },
            ),
        }
    )
    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            valid_for = timedelta(minutes=15)
            try:
                user = USER.objects.get(email__iexact=email)
            except USER.DoesNotExist as e:
                raise ValidationError({"error": "User not found"}) from e

            # Delete any existing password reset tokens for the user
            VerificationToken.objects.filter(user=user, type=VerificationTypeChoices.PASSWORD_RESET).delete()
            verification_token = VerificationToken.objects.create(
                user=user,
                type=VerificationTypeChoices.PASSWORD_RESET,
                valid_for=valid_for,
            )

            send_email.delay(
                subject="Password Reset",
                template_name="users/password_reset_email.html",
                from_email=None,
                recipient_list=[user.email],
                context={
                    "title": "Password Reset",
                    "token": verification_token.token,
                    "password_reset_url": PASSWORD_RESET_URL,
                },
            )
            return Response({"message": "Password reset email sent"}, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

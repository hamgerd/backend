from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from drf_yasg.openapi import Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework_simplejwt.tokens import RefreshToken

from config.settings.base import EMAIL_VERIFICATION_URL, PASSWORD_RESET_URL
from core.tasks.email import send_email
from users.models import User
from users.serializers.me import UserMESerializer
from users.serializers.user import PasswordResetRequestSerializer, PasswordResetSerializer, UserRegistrationSerializer,UserSerializer
from verification.choices import VerificationTypeChoices
from verification.models import VerificationToken


class UserMeView(GenericAPIView):
    serializer_class = UserMESerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserMESerializer(request.user)
        return Response(serializer.data)


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
            user: User = serializer.create(serializer.validated_data)
            self._add_refresh_token_to_serializer_context(serializer, user)
            verification_token = self._create_email_verification_token(user)
            transaction.on_commit(lambda: self._send_verification_email(user, verification_token))
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    @staticmethod
    def _add_refresh_token_to_serializer_context(serializer, user):
        token = RefreshToken.for_user(user)
        serializer.context["refresh_token"] = str(token)

    @staticmethod
    def _send_verification_email(user, verification_token):
        send_email.delay(
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

    @staticmethod
    def _create_email_verification_token(user):
        return VerificationToken.objects.create(
            user=user,
            type=VerificationTypeChoices.EMAIL,
            expire_at=timezone.now() + timedelta(minutes=15),
        )


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
            user = User.get_by_email(email)
            verification_token = self.create_password_reset_token(user)
            self.send_password_reset_email(user, verification_token)
            return Response({"message": "Password reset email sent"}, status=HTTP_201_CREATED)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    @staticmethod
    def send_password_reset_email(user, verification_token):
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

    @staticmethod
    def create_password_reset_token(user):
        VerificationToken.objects.filter(user=user, type=VerificationTypeChoices.PASSWORD_RESET).delete()

        return VerificationToken.objects.create(
            user=user,
            type=VerificationTypeChoices.PASSWORD_RESET,
            expire_at=timezone.now() + timedelta(minutes=15),
        )


class PasswordResetView(GenericAPIView):
    """
    Password reset view
    """

    serializer_class = PasswordResetSerializer
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
                    "errors": Schema(type="object", additional_properties=Schema(type="string")),
                },
            ),
        }
    )
    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data["token"]
            password = serializer.validated_data["password"]

            try:
                token_instance = VerificationToken.objects.get(token=token)
            except VerificationToken.DoesNotExist as e:
                raise ValidationError({"error": "Token invalid or expired"}) from e

            if token_instance.is_expired:
                raise ValidationError({"error": "Token expired"})

            token_instance.user.set_password(password)
            token_instance.user.save()
            token_instance.delete()
            return Response({"message": "Password changes successfully"}, status=HTTP_201_CREATED)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

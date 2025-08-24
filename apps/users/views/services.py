from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.tasks.email import send_email
from apps.verification.choices import VerificationTypeChoices
from apps.verification.models import VerificationToken
from config.settings.base import EMAIL_VERIFICATION_URL

from ..models import User


class UserRegisterService:
    def register(self, serializer):
        user: User = serializer.create(serializer.validated_data)
        self._add_refresh_token_to_serializer_context(serializer, user)
        self.send_register_verification_email(user)

    def send_register_verification_email(self, user):
        verification_token = self.create_email_verification_token(user)
        transaction.on_commit(lambda: self._send_verification_email(user, verification_token))

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
    def create_email_verification_token(user):
        return VerificationToken.objects.create(
            user=user,
            type=VerificationTypeChoices.EMAIL,
            expire_at=timezone.now() + timedelta(days=2),
        )

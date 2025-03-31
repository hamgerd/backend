from datetime import timedelta

from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from config.settings.base import EMAIL_VERIFICATION_URL
from core.tasks.email import send_email
from users.serializers.user import UserRegistrationSerializer
from verification.choices import VerificationTypeChoices
from verification.models import VerificationToken


class UserRegisterView(GenericAPIView):
    """
    Register a new user and send a verification email
    """

    serializer_class = UserRegistrationSerializer

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
                        "expiration": valid_for.total_seconds(),
                        "domain": EMAIL_VERIFICATION_URL,
                    },
                )
            )
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

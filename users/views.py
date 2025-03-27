from datetime import timedelta

from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from users.serializer import UserRegistrationSerializer
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
            verification_token = VerificationToken.objects.create(
                user=user,
                type=VerificationTypeChoices.EMAIL,
                valid_for=timedelta(minutes=15),
            )
            return Response(serializer.data, status=HTTP_201_CREATED)

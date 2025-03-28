from drf_yasg.openapi import Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from verification.models import VerificationToken


class EmailVerifyView(APIView):
    """
    Verify email using the token
    """

    @swagger_auto_schema(
        responses={
            HTTP_200_OK: Schema(
                type="object", properties={"message": Schema(type="string", description="Success message")}
            ),
            HTTP_400_BAD_REQUEST: Schema(
                type="object", properties={"error": Schema(type="string", description="Error message")}
            ),
        }
    )
    def get(self, request, token: str):
        token = VerificationToken.objects.filter(token=token).first()
        if not token:
            return Response({"error": "Invalid token"}, status=HTTP_400_BAD_REQUEST)
        if not token.is_valid:
            return Response({"error": "Token expired"}, status=HTTP_400_BAD_REQUEST)

        token.user.is_active = True
        token.user.save()
        token.delete()

        return Response({"message": "Email verified successfully"}, status=HTTP_200_OK)

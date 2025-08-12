from rest_framework import status
from rest_framework.exceptions import APIException


class BadRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid request parameters"
    default_code = "BadRequestException"

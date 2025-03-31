from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext
from rest_framework.exceptions import ValidationError


class User(AbstractUser):
    email = models.EmailField(gettext("email address"), unique=True)

    @classmethod
    def get_by_email(cls, email: str):
        try:
            return User.objects.get(email__iexact=email)
        except User.DoesNotExist as e:
            raise ValidationError({"error": "User not found"}) from e

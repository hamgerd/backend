from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext
from rest_framework.exceptions import ValidationError

from core.utils.identicon import add_profile_picture


class User(AbstractUser):
    email = models.EmailField(gettext("email address"), unique=True)
    phone_number = models.CharField(max_length=11, blank=True, null=True, validators=[RegexValidator(r"^09\d{9}$")])
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True)

    def save(self, *args, **kwargs):
        add_profile_picture(self)
        super().save(*args, **kwargs)

    @classmethod
    def get_by_email(cls, email: str):
        try:
            return User.objects.get(email__iexact=email)
        except User.DoesNotExist as e:
            raise ValidationError({"error": "User not found"}) from e

from django.db import models


class VerificationTypeChoices(models.TextChoices):
    EMAIL = "email", "Email"
    PASSWORD_RESET = "password_reset", "Password Reset"

from django.db import models


class VerificationTypeChoices(models.TextChoices):
    EMAIL = "email", "Email"

from random import randbytes

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel
from apps.verification.choices import VerificationTypeChoices

USER = get_user_model()


def generate_token():
    return randbytes(32).hex()


class VerificationToken(BaseModel):
    """
    Model to store verification tokens for users
    """

    token = models.CharField(max_length=64, default=generate_token, editable=False)
    user = models.ForeignKey(to=USER, on_delete=models.CASCADE, related_name="verification_tokens")
    type = models.CharField(max_length=20, choices=VerificationTypeChoices.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user}'s {self.type} token"

    @property
    def is_expired(self):
        """
        Checks if the token is expired
        """
        return self.expire_at < timezone.now()

    class Meta:
        ordering = ["-created_at"]

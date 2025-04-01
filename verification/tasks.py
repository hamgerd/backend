from celery import shared_task
from django.utils import timezone

from verification.models import VerificationToken


@shared_task
def auto_delete_expired_verification_tokens():
    """
    Delete expired verification tokens
    """

    expired_tokens = VerificationToken.objects.filter(expire_at__lt=timezone.now())
    deleted_count, _ = expired_tokens.delete()
    return f"Deleted {deleted_count} expired tokens"

from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.cache import cache
from django.core.validators import MinLengthValidator
from django.db import models

from apps.core.models import BaseModel
from apps.core.utils.identicon import add_default_image


class Organization(BaseModel):
    name = models.CharField(max_length=255)
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator(), MinLengthValidator(3, "Username must be at least 3 characters long")],
    )
    logo = models.ImageField(upload_to="organizations/images/", blank=True)
    description = models.CharField(max_length=256, blank=True)
    long_description = models.TextField(blank=True)
    email = models.EmailField(blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organizations")
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def event_count(self) -> int:
        key = f"{self.username}:event-count"
        event_count_data = cache.get(key)
        if not event_count_data:
            event_count_data = self.events.count()
            cache.set(key, event_count_data, timeout=60 * 60 * 12)

        return event_count_data

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.logo:
            add_default_image(self, image_field_name="logo")
        super().save(*args, **kwargs)
